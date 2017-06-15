extern crate hound;
extern crate stft;
extern crate num_cpus;

use stft::{STFT, WindowType};
use std::f64;

use std::sync::{Arc, Mutex};
use std::thread;

use std::os::raw;
use std::ffi::CStr;
use std::slice;

type Column = Vec<raw::c_double>;
type Spectrogram = Vec<Column>;

#[repr(C)]
pub struct FFI_Spectrogram {
    data : *const *const raw::c_double,
    shape : (u64, u64),
}

#[no_mangle]
pub extern fn spectrogram( file_name: *const raw::c_char, 
                           window_size: raw::c_uint, 
                           step_size : raw::c_uint ) -> *const raw::c_void
{
    unsafe
    {
        let name: String = CStr::from_ptr(file_name).to_string_lossy().into_owned();
        let mut reader = hound::WavReader::open(name).unwrap();
        let audio_data : Vec<f64> = reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();  
        
        let s = get_spectrogram(&audio_data, window_size as usize, step_size as usize);
        let p_array : Vec<*const raw::c_double> = 
            s.iter().map(|c| Box::into_raw(c.clone().into_boxed_slice()) as *const raw::c_double).collect();
        
        let spect = FFI_Spectrogram {
            shape : (s.len() as u64, s[0].len() as u64),
            data : Box::into_raw(p_array.into_boxed_slice()) as *const *const raw::c_double
        };

        Box::into_raw(Box::new(spect)) as *const raw::c_void
    }
}

#[no_mangle]
pub extern fn clean( ptr : *const raw::c_void) 
{
    unsafe 
    { 
        let ffi_spect = Box::from_raw(ptr as *mut FFI_Spectrogram);
        let mut data = slice::from_raw_parts(ffi_spect.data, ffi_spect.shape.0 as usize);
        for x in 0..data.len() {
            Box::from_raw(data[x] as *mut f64);
        }
    }
}

fn get_spectrogram(audio_data : &Vec<f64>, window_size: usize, step_size: usize) -> Spectrogram
{ 
    let cpu_count = num_cpus::get();
    let audio_len = audio_data.len();

    let mut thread_handles : Vec<thread::JoinHandle<_>> = Vec::new();
    let sub_spects = Arc::new(Mutex::new(vec![Spectrogram::new(); cpu_count]));

    for (index,audio_slice) in audio_data.chunks(audio_len/cpu_count).enumerate() 
    {
        let slice = audio_slice.to_vec();
        let sub_spects = sub_spects.clone();
        let handle : thread::JoinHandle<_> = thread::spawn(move || 
        {
            let s = sub_spect(&slice, window_size, step_size);
            let mut sub_spects = sub_spects.lock().unwrap();
            sub_spects[index] = s; 
        });

        thread_handles.push(handle);
    }

    for handle in thread_handles {
        assert!(handle.join().is_ok());
    }

    let mut final_spectrogram : Spectrogram = Vec::new();
    let sub_spects = sub_spects.lock().unwrap();

    for part in sub_spects.iter() {
        let mut part = part.clone();
        final_spectrogram.append(&mut part);
    }

    return final_spectrogram;
}

fn sub_spect(audio_data : &Vec<f64>, window_size: usize, step_size: usize) -> Spectrogram
{
    let spectrogram_len = (audio_data.len()-(window_size-step_size))/step_size;
    let mut spectrogram : Spectrogram = vec![Vec::new(); spectrogram_len];
    let mut stft = STFT::<f64>::new(WindowType::Hanning, window_size, step_size);

    stft.append_samples(audio_data);
    
    let mut column_number = 0;
    while stft.contains_enough_to_compute() 
    {
        let mut spectrogram_column: Column =
            std::iter::repeat(0.).take(stft.output_size()).collect();
        stft.compute_column(&mut spectrogram_column[..]);
        spectrogram[column_number] = spectrogram_column[..1500].to_vec();;
        column_number += 1;
        
        //println!("{}", column_number);
        stft.move_to_next_column();
    }

    return spectrogram;
}

/*
fn get_frequency(v : &Vec<f64>) -> usize {

    let mut frequency : usize = 0;
    let mut amplitude : f64 = 0.0;

    let mut index : usize = 0;            
    for value in v {
        if value > &amplitude {
            amplitude = *value;
            frequency = index;
        }

        index += 1;
    }

    frequency
}

fn get_pitch<'a>(frequency : &'a f64) -> String {

    if frequency.round() as i32 == 0 { 
        return String::from("-");
    }

    let notes = vec![ "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B" ];
    
    let log_base : f64 = (2.0 as f64).powf(1.0/12.0); 
    
    //distance to A440 of the note
    let mut offset : i32 = ((frequency / 440.0).log(log_base)).round() as i32; 
    
    //adjust offset for the array
    offset += if offset >= 0 {9} else {-2}; 

    let note_index : usize = if offset >= 0 {offset%12} else {11 + offset%12} as usize;
    format!( "{note}{octave}", note = notes[note_index], octave = 4 + offset/12) 
} */