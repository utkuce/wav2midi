extern crate stft;
extern crate num_cpus;

use std::f64;
use self::stft::{STFT, WindowType};
use std::sync::{Arc, Mutex};
use std::thread;

type Column = Vec<::std::os::raw::c_double>;
type Spectrogram = Vec<Column>;

pub fn get_spectrogram(audio_data : &Vec<f64>, window_size: usize, step_size: usize,
                       highpass: usize, lowpass: usize) -> Spectrogram
{ 
    let cpu_count = num_cpus::get();
    let audio_len = audio_data.len();
    
    let mut thread_handles : Vec<thread::JoinHandle<_>> = Vec::new();
    let sub_spects = Arc::new(Mutex::new(vec![Spectrogram::new(); cpu_count]));
    
    let overlap_size = window_size-step_size;    
    let mut slice : Vec<f64> = Vec::new();
    let chunk_size = (audio_len as f64 / cpu_count as f64).ceil();
    for (index,audio_slice) in audio_data.chunks(chunk_size as usize).enumerate() 
    {
        slice.extend_from_slice(audio_slice);
        let sub_spects = sub_spects.clone();
        let mut s = slice.clone();
        let handle : thread::JoinHandle<_> = thread::spawn(move || 
        {
            s = ::filters::apply_filters(&s, highpass, lowpass);
            let s = sub_spect(&s, window_size, step_size);
            let mut sub_spects = sub_spects.lock().unwrap();
            sub_spects[index] = s; 
        });

        thread_handles.push(handle);
        let slice_len = audio_slice.len()-1;
        slice = audio_slice[slice_len-overlap_size..slice_len].to_vec();
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
        let mut spectrogram_column: Column = ::std::iter::repeat(0.).take(stft.output_size()).collect();
        stft.compute_column(&mut spectrogram_column[..]);
        spectrogram[column_number] = spectrogram_column.to_vec();
        column_number += 1;
        
        //println!("{}", column_number);
        stft.move_to_next_column();
    }

    return spectrogram;
}