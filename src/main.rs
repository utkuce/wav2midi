extern crate hound;
extern crate stft;
extern crate csv;
extern crate num_cpus;

use stft::{STFT, WindowType};
use std::f64;

use std::io::prelude::Write;
use std::fs::File;

use std::sync::{Arc, Mutex};
use std::thread;

fn main() {

    let mut reader = hound::WavReader::open("tetris2.wav").unwrap();
    let audio_data : Vec<f64> = 
        reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();    

    let mut file = match File::create("rhythm.csv") {
        Err(_) => panic!("couldn't create file"),
        Ok(file) => file,
    };

    let spectrogram = get_spectrogram(&audio_data, 4096, 512);

    let mut csv_writer = csv::Writer::from_memory();
    for column in spectrogram {
        assert!(csv_writer.encode(column).is_ok());
    }
    assert!(file.write_all(csv_writer.as_bytes()).is_ok());

    //write_spectrogram_data(&audio_data, reader.spec().sample_rate, 512, "pitch.csv");
}

fn get_spectrogram(audio_data : &Vec<f64>, window_size: usize, step_size: usize) -> Vec<Vec<f64>>
{
    let spectrogram_len = (audio_data.len()-(window_size-step_size))/step_size;
    let mut spectrogram : Vec<Vec<f64>> = Vec::new();
 
    let cpu_count = num_cpus::get();
    let audio_len = audio_data.len();
    
    for audio_slice in audio_data.chunks(audio_len/cpu_count) 
    {
        spectrogram.append(&mut sub_spect(&audio_slice.to_vec(), window_size, step_size));
    }

    spectrogram.shrink_to_fit();
    return spectrogram;
}

fn sub_spect(audio_data : &Vec<f64>, window_size: usize, step_size: usize) -> Vec<Vec<f64>>
{
    let spectrogram_len = (audio_data.len()-(window_size-step_size))/step_size;
    let mut spectrogram : Vec<Vec<f64>> = vec![Vec::new(); spectrogram_len];
    let mut stft = STFT::<f64>::new(WindowType::Hanning, window_size, step_size);

    stft.append_samples(audio_data);
    
    let mut column_number = 0;
    while stft.contains_enough_to_compute() 
    {
        let mut spectrogram_column: Vec<f64> =
            std::iter::repeat(0.).take(stft.output_size()).collect();
        stft.compute_column(&mut spectrogram_column[..]);

        println!("{}/{}", column_number, spectrogram_len-1);
        spectrogram[column_number] = spectrogram_column[..1500].to_vec();        
        column_number += 1;
        
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