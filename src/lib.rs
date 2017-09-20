extern crate hound;
extern crate synthrs;

use std::f64;
use std::os::raw;

mod spectrogram;
mod filters;

#[repr(C)]
pub struct FFI_Spectrogram {
    data : *const *const raw::c_double,
    shape : (u64, u64),
}

#[no_mangle]
pub extern fn spectrogram( file_name: *const raw::c_char,  window_size: raw::c_uint, step_size : raw::c_uint,
                           highpass: usize, lowpass: usize) -> *const raw::c_void
{
    unsafe
    {
        let name: String = std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned();
        let mut reader = hound::WavReader::open(name).unwrap();
        let audio_data : Vec<f64> = reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();

        print!("STFT: {{ Window Size: {} Step Size: {} }}, audio: {{ ", window_size, step_size);
        print!("Duration: {} seconds, ", reader.duration() / reader.spec().sample_rate);
        print!("Sample Rate: {}, ", reader.spec().sample_rate);
        print!("Channels: {}, ", reader.spec().channels);
        println!("Bit Depth: {} }}", reader.spec().bits_per_sample);        
        
        let s = spectrogram::get_spectrogram(&audio_data, window_size as usize, step_size as usize,
                                             highpass, lowpass);
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
        let data = std::slice::from_raw_parts(ffi_spect.data, ffi_spect.shape.0 as usize);
        for x in 0..data.len() {
            Box::from_raw(data[x] as *mut f64); 
        }
    }
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