#![feature(step_by)]
#![allow(dead_code)]
#![allow(deprecated)]
#![feature(use_extern_macros)]

extern crate hound;
extern crate arrayfire;

use arrayfire::{Array, Dim4};
use std::collections::HashMap;

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

type Spectrogram = Vec<Array>;

pub struct AudioFile {
    name : String,
    data : Array,
    spectrograms : Option<HashMap<String, Spectrogram>>,
    max_frequncies : Option<Array>, 
}

#[no_mangle]
pub fn analyze(file_name: *const raw::c_char ) -> *const raw::c_void
{
    println!("Active Backend: {}", arrayfire::get_active_backend());
    
    println!("reading file...");
    let name: String = unsafe{std::ffi::CStr::from_ptr(file_name)}.to_string_lossy().into_owned();
    let mut reader = hound::WavReader::open(name.clone()).unwrap();
    let data : Vec<f64> = reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();
    
    let mut data_af = Array::new(&data, Dim4::new(&[data.len() as u64,1,1,1])); 

    println!("applying filters...");
    data_af = ::filters::highpass(data_af, 215);
    //data_af = ::filters::lowpass(data_af, 500);

    println!("calculating narrowband spectrogram...");
    let narrowband = spectrogram::get_spectrogram(data_af.clone(), 4096, 256);

    println!("calculating wideband spectrogram...");
    let wideband = spectrogram::get_spectrogram(data_af, 44100, 2048);

    println!("combining spectrograms...");
    let combined = spectrogram::combine(narrowband, wideband);

    println!("calculating harmonic product spectrum...");
    let hps = spectrogram::harmonic_product_spectrum(combined, 7);

    println!("transfering data to the host...");

    let s = spectrogram::to_host(hps);

    let p_array : Vec<*const raw::c_double> = 
        s.iter().map(|c| Box::into_raw(c.clone().into_boxed_slice()) as *const raw::c_double).collect();
        
    let spect = FFI_Spectrogram {
        shape : (s.len() as u64, s[0].len() as u64),
        data : Box::into_raw(p_array.into_boxed_slice()) as *const *const raw::c_double
    };

    Box::into_raw(Box::new(spect)) as *const raw::c_void

    //AudioFile { name: name, data: data_af, spectrograms: None, max_frequncies: None}
}

#[no_mangle]
pub extern fn clean( ptr : *const raw::c_void) 
{
    unsafe 
    { 
        let ffi_spect = Box::from_raw(ptr as *mut FFI_Spectrogram);
        let data = std::slice::from_raw_parts(ffi_spect.data, ffi_spect.shape.0 as usize);
        for x in 0..data.len() { Box::from_raw(data[x] as *mut f64); }
    }
}

#[no_mangle]
pub extern fn print_audio_details(file_name: *const raw::c_char) 
{
    let name: String = unsafe { std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned() };
    let reader = hound::WavReader::open(name).unwrap();

    print!("Audio: {{ Duration: {} seconds, ", reader.duration() / reader.spec().sample_rate);
    print!("Sample Rate: {}, ", reader.spec().sample_rate);
    print!("Channels: {}, ", reader.spec().channels);
    println!("Bit Depth: {} }}", reader.spec().bits_per_sample);
}

#[no_mangle]
pub extern fn write_midi(frequencies: *const raw::c_double, len: raw::c_uint, file_name: *const raw::c_char)
{
    let name: String = unsafe { std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned() };
    let reader = hound::WavReader::open(name.clone()).unwrap();

    // division = 1 beat = 1 seconds
    let seconds = reader.duration() as f64 / reader.spec().sample_rate as f64;
    let division : i16 = (len as f64 / seconds) as i16;
    let notes = postprocess::get_notes(frequencies, len);
    
    let n = String::from(Path::new(name.as_str()).file_stem().unwrap().to_str().unwrap());
    let song = postprocess::Song {notes: notes, name: n, division: division};

    println!("{}", song);
    postprocess::write_midi(song);
}