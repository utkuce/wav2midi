use synthrs::filter::{convolve, cutoff_from_frequency, bandpass_filter, highpass_filter};

/*
pub fn bandpass(audio_data: &Vec<f64>, h: usize, l: usize) -> Vec<f64>
{
    let highpass = cutoff_from_frequency(h as f64, 44100);
    let lowpass = cutoff_from_frequency(l as f64, 44100);
    let bandpass = bandpass_filter(highpass, lowpass, 0.01);
    convolve(&bandpass, &audio_data)
}
*/

pub fn highpass(audio_data: &Vec<f64>, h: usize) -> Vec<f64>
{
    let highpass = highpass_filter(cutoff_from_frequency(h as f64, 44100), 0.01);
    convolve(&highpass, &audio_data)
}