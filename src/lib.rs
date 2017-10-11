extern crate hound;
extern crate synthrs;
extern crate rimd;

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
pub extern fn spectrogram( file_name: *const raw::c_char, 
                           window_size: raw::c_uint, step_size : raw::c_uint) -> *const raw::c_void
{
    unsafe
    {
        let name: String = std::ffi::CStr::from_ptr(file_name).to_string_lossy().into_owned();
        let mut reader = hound::WavReader::open(name).unwrap();
        let audio_data : Vec<f64> = 
            reader.samples::<i16>().map(|sample| sample.unwrap() as f64).collect();
        
        let s = spectrogram::get_spectrogram(&audio_data, window_size as usize, step_size as usize);
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