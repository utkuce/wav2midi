#![feature(step_by)]
#![allow(dead_code)]
#![allow(deprecated)]
#![feature(use_extern_macros)]

extern crate hound;
extern crate arrayfire;

use arrayfire::{Array, Dim4};

use std::f64;
use std::os::raw;
use std::path::Path;

mod spectrogram;
mod filters;
mod postprocess;

#[repr(C)]
pub struct FFI_Spectrogram {
    data : *const *const raw::c_double,
    shape : (u64, u64),
}

#[no_mangle]
pub fn analyze(file_name: *const raw::c_char, draw_results: bool ) -> *const *const raw::c_void
{
    //arrayfire::set_backend(arrayfire::Backend::CPU);
    println!("Active Backend: {}", arrayfire::get_active_backend());
    
    println!("reading file...");
    let name: String = unsafe{std::ffi::CStr::from_ptr(file_name)}.to_string_lossy().into_owned();
    let mut reader = hound::WavReader::open(name.clone()).unwrap();

    print!("Audio: {{ Duration: {} seconds, ", reader.duration() / reader.spec().sample_rate);
    print!("Sample Rate: {}, ", reader.spec().sample_rate);
    print!("Channels: {}, ", reader.spec().channels);
    println!("Bit Depth: {} }}", reader.spec().bits_per_sample);

    let data : Vec<f64> = reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();
    let mut data_af = Array::new(&data, Dim4::new(&[data.len() as u64,1,1,1])); 
  
    println!("applying preprocess filters..."); // TODO: filters as parameters
    data_af = ::filters::highpass(data_af, 215);
    //data_af = ::filters::lowpass(data_af, 200);

    println!("calculating narrowband spectrogram...");
    let narrowband = spectrogram::get_spectrogram(&data_af, 8192, 1024);
    println!("calculating wideband spectrogram...");
    let wideband = spectrogram::get_spectrogram(&data_af, 44100, 1024);
    println!("combining spectrograms...");
    let combined = spectrogram::combine(&narrowband, &wideband);
    println!("calculating harmonic product spectrum...");
    let hps = spectrogram::harmonic_product_spectrum(combined.clone(), 3); // TODO: hps rate as parameter

    let frequencies = spectrogram::get_frequencies(hps.clone());

    println!("onset detection...");    
    let complex = spectrogram::stft(&data_af, 8192, 1024);
    let complex_df = spectrogram::onset_detection(&complex);

    let mut graphs = Vec::<*const raw::c_void>::new();    
    if draw_results 
    {
        graphs.push(to_ffi(&spectrogram::to_host(narrowband)));
        graphs.push(to_ffi(&spectrogram::to_host(wideband)));
        graphs.push(to_ffi(&spectrogram::to_host(combined)));
        graphs.push(to_ffi(&spectrogram::to_host(hps)));
        
        let mut frequencies_host : Vec<raw::c_uint> = vec![0; frequencies.elements()];
        frequencies.host(frequencies_host.as_mut_slice());
        let f_pointer = Box::into_raw(frequencies_host.into_boxed_slice()) as *const raw::c_uint;
        graphs.push(f_pointer as *const raw::c_void);

        let pointer = Box::into_raw(complex_df.into_boxed_slice()) as *const raw::c_double;
        graphs.push(pointer as *const raw::c_void);        
    }

    println!("writing midi...");
    write_midi(frequencies, name);

    arrayfire::device_gc();

    println!("Analysis completed.");
    Box::into_raw(graphs.into_boxed_slice()) as *const *const raw::c_void
}

fn to_ffi(s : &Vec<Vec<f64>>) -> *const raw::c_void
{
    let p_array : Vec<*const raw::c_double> = 
        s.iter().map(|c| Box::into_raw(c.clone().into_boxed_slice()) as *const raw::c_double).collect();
        
    let spect = FFI_Spectrogram {
        shape : (s.len() as u64, s[0].len() as u64),
        data : Box::into_raw(p_array.into_boxed_slice()) as *const *const raw::c_double
    };

    Box::into_raw(Box::new(spect)) as *const raw::c_void
}

#[no_mangle]
pub extern fn clean2d( ptr : *const raw::c_void) 
{
    unsafe 
    { 
        let ffi_spect = Box::from_raw(ptr as *mut FFI_Spectrogram);
        let data = std::slice::from_raw_parts(ffi_spect.data, ffi_spect.shape.0 as usize);
        for x in 0..data.len() { Box::from_raw(data[x] as *mut f64); }
    }
}

#[no_mangle]
pub extern fn clean1d( ptr : *const raw::c_void)
{
    unsafe { Box::from_raw(ptr as *mut raw::c_double) };
}

pub extern fn print_audio_details(file_name: *const raw::c_char) 
{
    let name: String = unsafe { std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned() };
    let reader = hound::WavReader::open(name).unwrap();

    print!("Audio: {{ Duration: {} seconds, ", reader.duration() / reader.spec().sample_rate);
    print!("Sample Rate: {}, ", reader.spec().sample_rate);
    print!("Channels: {}, ", reader.spec().channels);
    println!("Bit Depth: {} }}", reader.spec().bits_per_sample);
}

fn write_midi(frequencies: Array, name: String)
{
    let reader = hound::WavReader::open(name.clone()).unwrap();

    // division = 1 beat = 1 seconds
    let seconds = reader.duration() as f64 / reader.spec().sample_rate as f64;
    let division : i16 = (frequencies.elements() as f64 / seconds) as i16;

    let mut host = vec![0; frequencies.elements()];    
    frequencies.host(host.as_mut_slice());
    let notes = postprocess::get_notes(host);
    
    let midi_name = String::from(Path::new(name.as_str()).file_stem().unwrap().to_str().unwrap());
    let song = postprocess::Song {notes: notes, name: midi_name, division: division};

    println!("{}", song);
    postprocess::write_midi(song);
}