#![feature(step_by)]
#![allow(dead_code)]
#![allow(deprecated)]
#![feature(use_extern_macros)]

extern crate hound;
extern crate arrayfire;

use arrayfire::{Array, Dim4, Seq};

use std::f64;
use std::os::raw;
use std::path::Path;
use std::slice;

mod spectrogram;
mod filters;
mod postprocess;

#[repr(C)]
pub struct FFI_Spectrogram {
    data : *const *const raw::c_double,
    shape : (u64, u64),
}

#[no_mangle]
pub fn analyze(file_name: *const raw::c_char, window_size: raw::c_uint, highpass: raw::c_uint, 
               hps_rate: raw::c_uint) -> *const *const raw::c_void
{
    println!("Active Backend: {}", arrayfire::get_active_backend());
    
    println!("reading file...");
    let name: String = unsafe{std::ffi::CStr::from_ptr(file_name)}.to_string_lossy().into_owned();
    let mut reader = hound::WavReader::open(name.clone()).unwrap();

    print_audio_details(&reader);

    let data : Vec<f64> = reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();
    let mut data_af = Array::new(&data, Dim4::new(&[data.len() as u64,1,1,1])); 
  
    println!("applying preprocess filters..."); // TODO: filters as parameters
    data_af = ::filters::highpass(data_af, highpass as usize);
    //data_af = ::filters::lowpass(data_af, 330);

    let mut graphs = Vec::<*const raw::c_void>::new();        

    println!("calculating narrowband spectrogram...");
    let window_size = (2. as f64).powi(window_size as i32) as usize;
    let complex = spectrogram::stft(&data_af, window_size, 1024);
    let narrowband = spectrogram::complex_to_magnitude(&complex);
    graphs.push(to_ffi(&spectrogram::to_host(&narrowband)));
    
    println!("calculating wideband spectrogram...");
    let wideband = spectrogram::get_spectrogram(&data_af, 44100, 1024);
    graphs.push(to_ffi(&spectrogram::to_host(&wideband)));

    println!("combining spectrograms...");
    let combined = spectrogram::combine(&narrowband, &wideband);
    graphs.push(to_ffi(&spectrogram::to_host(&combined)));    

    println!("calculating harmonic product spectrum...");
    let hps = spectrogram::harmonic_product_spectrum(combined, hps_rate);
    graphs.push(to_ffi(&spectrogram::to_host(&hps)));    

    println!("getting frequencies...");
    let frequencies = spectrogram::get_frequencies(&hps);
    let mut frequencies_host : Vec<raw::c_uint> = vec![0; frequencies.elements()];
    frequencies.host(frequencies_host.as_mut_slice());
    let freq_p = Box::into_raw(frequencies_host.into_boxed_slice()) as *const raw::c_uint;
    graphs.push(freq_p as *const raw::c_void);

    println!("onset detection function...");
    let phase = spectrogram::complex_to_phase(&complex);
    let complex_df = spectrogram::onset_detection(&narrowband, &phase);
    let detect_p = Box::into_raw(complex_df.into_boxed_slice()) as *const raw::c_double;
    graphs.push(detect_p as *const raw::c_void);

    println!("Analysis completed.");    
    arrayfire::device_gc();

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

fn post_filter(spectrogram: &Array, above: usize, below: usize) -> Array
{
    let sequence0 = Seq::new(above as u32, below as u32, 1);
    let sequence1 = Seq::new(0, (spectrogram.dims()[1]-1) as u32, 1);
    let mut idxr = arrayfire::Indexer::new();            
    idxr.set_index(&sequence0, 0, Some(true));
    idxr.set_index(&sequence1, 1, Some(true));    
  
    arrayfire::index_gen(&spectrogram, idxr)
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

fn print_audio_details(reader: &hound::WavReader<std::io::BufReader<std::fs::File>>) 
{
    print!("Audio: {{ Duration: {} seconds, ", reader.duration() / reader.spec().sample_rate);
    print!("Sample Rate: {}, ", reader.spec().sample_rate);
    print!("Channels: {}, ", reader.spec().channels);
    println!("Bit Depth: {} }}", reader.spec().bits_per_sample);
}

#[no_mangle]
pub extern fn create_midi(frequencies: *mut raw::c_uint, f_len: raw::c_uint,
                           onsets: *mut raw::c_double, o_len: raw::c_uint, 
                           file_name: *const raw::c_char)
{
    let name: String = unsafe { std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned() };
    let reader = hound::WavReader::open(&name).unwrap();
    
    // division = 1 beat = 1 seconds
    let seconds = reader.duration() as f64 / reader.spec().sample_rate as f64;
    let division : i16 = (f_len as f64 / seconds) as i16;

    let f : &[u32] = unsafe { slice::from_raw_parts(frequencies, f_len as usize) };
    let o : &[f64] = unsafe { slice::from_raw_parts(onsets, o_len as usize) };    

    let notes = postprocess::get_notes(&f.to_vec(), &o.to_vec());
    
    let midi_name = String::from(Path::new(name.as_str()).file_stem().unwrap().to_str().unwrap());
    let song = postprocess::Song {notes: notes, name: midi_name, division: division};

    println!("{}", song);
    postprocess::write_midi(song);
}