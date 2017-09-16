use synthrs::filter::{convolve, cutoff_from_frequency, bandpass_filter};

pub fn apply_filters(audio_data: &Vec<f64>) -> Vec<f64>
{
    let highpass = cutoff_from_frequency(210.0, 44100);
    let lowpass = cutoff_from_frequency(450.0, 44100);
    let bandpass = bandpass_filter(highpass, lowpass, 0.01);
    convolve(&bandpass, &audio_data)
}