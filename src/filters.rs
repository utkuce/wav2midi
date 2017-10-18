extern crate synthrs;
use self::synthrs::filter::{cutoff_from_frequency, highpass_filter};
use arrayfire::{Array, Dim4, convolve1, ConvMode, ConvDomain};

pub fn highpass(signal: Array, h: usize) -> Array
{
    let highpass = highpass_filter(cutoff_from_frequency(h as f64, 44100), 0.01); 
    let filter : Array = Array::new(&highpass, Dim4::new(&[highpass.len() as u64,1,1,1]));
    convolve1(&signal, &filter, ConvMode::DEFAULT, ConvDomain::FREQUENCY)
}