extern crate synthrs;
use self::synthrs::filter::{cutoff_from_frequency, highpass_filter, lowpass_filter};
use arrayfire::{Array, Dim4, convolve1, ConvMode, ConvDomain};

pub fn highpass(signal: Array<f64>, h: usize) -> Array<f64>
{
    let highpass = highpass_filter(cutoff_from_frequency(h as f64, 44100), 0.01); 
    let filter : Array<f64> = Array::new(&highpass, Dim4::new(&[highpass.len() as u64,1,1,1]));
    convolve1(&signal, &filter, ConvMode::DEFAULT, ConvDomain::FREQUENCY)
}

pub fn lowpass(signal: Array<f64>, l: usize) -> Array<f64>
{
    let lowpass = lowpass_filter(cutoff_from_frequency(l as f64, 44100), 0.01);
    let filter : Array<f64> = Array::new(&lowpass, Dim4::new(&[lowpass.len() as u64,1,1,1]));
    convolve1(&signal, &filter, ConvMode::DEFAULT, ConvDomain::FREQUENCY)
}