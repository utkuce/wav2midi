extern crate stft;
extern crate num_cpus;

extern crate arrayfire;
extern crate num_complex;
extern crate apodize;

use self::arrayfire::{Array, Dim4, print_gen};
use self::num_complex::Complex;
use self::apodize::{hanning_iter};

use std::f64;
use self::stft::{STFT, WindowType};
use std::sync::{Arc, Mutex};
use std::thread;

type Column = Vec<::std::os::raw::c_double>;
type Spectrogram = Vec<Column>;

pub fn get_spectrogram(audio_data : &Vec<f64>, window_size: usize, step_size: usize) -> Spectrogram
{
    let mut spectrogram_af : Vec<Array> = Vec::new();
    for values in audio_data.windows(window_size).step_by(step_size)
    {
        let dim = Dim4::new(&[values.len() as u64, 1, 1, 1]);
        let windowing = Array::new(&hanning_iter(values.len()).collect::<Vec<f64>>(), dim);
        let values_af = Array::new(&values, dim);
        
        let input = values_af * windowing;
        let output : Array = arrayfire::fft(&input, 1.0, window_size as i64);
        spectrogram_af.push(output);
    }

    let cpu_count = num_cpus::get();
    let mut thread_handles : Vec<thread::JoinHandle<(usize, Spectrogram)>> = Vec::new();    
    let chunk_size = (spectrogram_af.len() as f32 / cpu_count as f32).ceil() as usize;

    for (index, piece) in spectrogram_af.chunks(chunk_size).enumerate()
    {  
        let owned_piece : Vec<Array> = Vec::from(piece);
        let handle : thread::JoinHandle<(usize, Spectrogram)> = thread::spawn(move || 
        {
            let mut sub_spect : Spectrogram = Vec::new();
            for column_af in owned_piece
            {
                let mut v = vec![Complex{re:0.0, im:0.0}; column_af.elements()];
                let slice : &mut [Complex<f64>] = v.as_mut_slice();
                column_af.host(slice);

                let half_column = slice[0..slice.len()/2].to_vec();                
                let mut column : Column = Vec::new();
                for complex in half_column { column.push(complex.unscale(10000.0).norm() as f64); }
                sub_spect.push(column);
            }

            return (index, sub_spect);
        });

        thread_handles.push(handle);         
    }

    let mut sub_spects : Vec<Spectrogram> = vec![Vec::new(); cpu_count];

    for handle in thread_handles 
    {
        let tuple : (usize, Spectrogram) = handle.join().unwrap(); 
        sub_spects[tuple.0] = tuple.1;
    }

    let mut final_spectrogram : Spectrogram = Vec::new();
    for part in sub_spects.iter() {
        let mut part = part.clone();
        final_spectrogram.append(&mut part);
    }
    return final_spectrogram;
}