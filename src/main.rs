extern crate hound;
extern crate stft;
extern crate csv;

use stft::{STFT, WindowType};
use std::f64;

use std::io::prelude::*;
use std::fs::File;

fn main() {

    let mut reader = hound::WavReader::open("tetris2.wav").unwrap(); 
    let audio_data : Vec<f64> = reader.samples::<i16>()
        .map(|sample| sample.unwrap() as f64).collect();

    let sample_rate: usize = reader.spec().sample_rate as usize;

    write_spectrogram_data(&audio_data, 4096, 512, "spectrogram1.csv");
    write_spectrogram_data(&audio_data, sample_rate, 512, "spectrogram2.csv");
}

fn write_spectrogram_data(audio_data : &Vec<f64>, window_size: usize, step_size: usize, file_name: &str) {

    let mut file = match File::create(&file_name) {
        Err(_) => panic!("couldn't create file"),
        Ok(file) => file,
    };
    let mut csv_writer = csv::Writer::from_memory();

    let mut stft = STFT::<f64>::new(WindowType::Hanning, window_size, step_size);
    let mut spectrogram_column: Vec<f64> =
        std::iter::repeat(0.).take(stft.output_size()).collect();

    let mut count : usize = 1;
    for some_samples in (&audio_data[..]).chunks(3000) {
        stft.append_samples(some_samples);

        while stft.contains_enough_to_compute() {

            stft.compute_column(&mut spectrogram_column[..]);
            let frequency : usize = get_frequency(&spectrogram_column);
            let pitch : String = get_pitch(&(frequency as f64));

            print!("Note:{p}, {f}Hz ", p=pitch, f=frequency);

            let result = csv_writer.encode(&spectrogram_column[..1500]); 
            assert!(result.is_ok());
            println!("{}/{}", count, 
                (audio_data.len()-(window_size-step_size)) /step_size );
            count +=1;
            stft.move_to_next_column();
        }
    }

    let result = file.write_all(csv_writer.as_bytes());
    assert!(result.is_ok());
}

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

    if frequency.round() as i32 == 0 { return String::from("-");}
    let notes = vec![ "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B" ];
    let log_base : f64 = (2.0 as f64).powf(1.0/12.0); 
    let mut offset : i32 = ((frequency / 440.0).log(log_base)).round() as i32; //distance to A440 of the note
    offset += if offset >= 0 {9} else {-2}; //adjust offset for the array
    let note_index : usize = if offset >= 0 {offset%12} else {11 + offset%12} as usize;
    format!( "{note}{octave}", note = notes[note_index], octave = 4 + offset/12) 
} 