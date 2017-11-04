extern crate apodize;

use arrayfire::*;
use self::apodize::{hanning_iter};
use std::f64;

type Column = Vec<f64>;
type Spectrogram = Vec<Column>;

pub fn get_spectrogram(audio_data : &Array, window_size: usize, step_size: usize) -> Array
{
    let array = stft(audio_data, window_size, step_size);

    let sequence0 = Seq::new(0, ((array.dims()[0] as f32 / 2.).floor()-1.) as u32, 1);
    let sequence1 = Seq::new(0, (array.dims()[1]-1) as u32, 1);    
    let mut idxr = Indexer::new();            
    idxr.set_index(&sequence0, 0, Some(true));
    idxr.set_index(&sequence1, 1, Some(true));    
    
    let half = index_gen(&array, idxr);

    complex_to_magnitude(&half)
}

pub fn complex_to_magnitude(stft: &Array) -> Array
{
    let spect_len = stft.dims()[1];
    let result = Array::new_empty(stft.dims(), DType::F64);

    for index in 0..spect_len
    {
        set_col(&result, &magnitude(&col(&stft, index)), index);
    }

    return result;
}

pub fn complex_to_phase(stft: &Array) -> Array
{
    let spect_len = stft.dims()[1];
    let result = Array::new_empty(stft.dims(), DType::F64);

    for index in 0..spect_len
    {
        set_col(&result, &phase(&col(&stft, index)), index);
    }

    return result;
}

pub fn stft(audio_data : &Array, window_size: usize, step_size: usize) -> Array
{
    let audio_len : usize = audio_data.elements();

    let spect_len : u64 = (( audio_len-(window_size-step_size) ) / step_size) as u64;
    let array = Array::new_empty(Dim4::new(&[window_size as u64, spect_len, 1,1]), DType::C64);

    let hanning_len = Dim4::new(&[window_size as u64,1,1,1]);
    let hanning = Array::new(&hanning_iter(window_size as usize).collect::<Vec<f64>>(), hanning_len);

    for (index, start) in (0..audio_len-window_size).step_by(step_size).enumerate()
    {
        let sequence =  Seq::new(start as u32, start as u32 + (window_size-1) as u32, 1);
        let mut idxr = Indexer::new();                
        idxr.set_index(&sequence, 0, Some(true));

        let new_col = fft(&(index_gen(&audio_data, idxr) * hanning.clone()), 1., window_size as i64);
        set_col(&array, &new_col, index as u64); 
    }

    return array;
}

fn magnitude(array : &Array) -> Array
{
    let magnitude = sqrt( &(pow(&real(&array),&2, true) * pow(&imag(&array),&2, true)) );
    floor(&log1p(&magnitude))
}

fn phase(array: &Array) -> Array
{
    atan2(&imag(array), &real(array), true)
}

pub fn onset_detection(complex: &Array) -> Vec<f64>
{
    let mut result : Vec<f64> = vec![0.,0.];

    let m = complex_to_magnitude(complex);
    let p = complex_to_phase(complex);

    let spect_len = complex.dims()[1];
    for index in 2..spect_len
    {
        let predicted_m = col(&m, index-1);
        let predicted_p = mul(&col(&p, index-1),&2, true) - col(&p, index-2);

        let a = col(&m, index) - predicted_m;
        let rectified = (&a + abs(&a))/2;
        let b = col(&p, index) - predicted_p;
        let distance = sqrt(&(pow(&rectified, &2, true) + pow(&b, &2, true))); 

        result.push(sum_all(&distance).0);
    }

    return result;
}
/*
pub fn spectral_flux(spectrogram: &Array) -> Vec<f64>
{
    let s = complex_to_magnitude(spectrogram);
    let mut result : Vec<f64> = Vec::new();
    let spect_len = spectrogram.dims()[1];
    for index in 0..spect_len-1
    {
        let diff = col(&s, index+1) - col(&s, index);
        let rectified = (&diff + abs(&diff))/2;
        let norm_sq = sum_all(&pow(&rectified, &2, true));
        result.push(norm_sq.0);
    }

    return result;
}

pub fn phase_deviation(spectrogram : &Array) -> Vec<f64>
{
    let s = complex_to_phase(spectrogram);
    let mut result : Vec<f64> = Vec::new();
    let spect_len = spectrogram.dims()[1];
    for index in 2..spect_len
    {
        let predicted = mul(&col(&s, index-1),&2, true) - col(&s, index-2);
        let diff = col(&s, index) - predicted;
        let norm_sq = mean_all(&pow(&diff, &2, true));
        result.push(norm_sq.0);
    }

    return result;
}
*/
pub fn combine(narrowband : &Array, wideband : &Array) -> Array
{
    let wd = wideband.dims();
    let narrow = resize(&narrowband, wd[0] as i64, wd[1] as i64, InterpType::BILINEAR);
    mul(wideband, &narrow, true)
}

pub fn harmonic_product_spectrum(combined : Array, rate : u32) -> Array
{
    let sequence0 = Seq::new(0 as u32, ((combined.dims()[0] as f32 / rate as f32)-1.) as u32, 1);
    let sequence1 = Seq::new(0 as u32, (combined.dims()[1]-1) as u32, 1);
    let mut idxr = Indexer::new();            
    idxr.set_index(&sequence0, 0, Some(true));
    idxr.set_index(&sequence1, 1, Some(true));    
  
    let mut hps = index_gen(&combined, idxr);

    for r in 2..rate+1
    {
        let scale = (combined.dims()[0] as f32 / r as f32) as i64;
        let downsampled = resize(&combined, scale, combined.dims()[1] as i64, InterpType::BILINEAR);

        let mut idxr = Indexer::new();            
        idxr.set_index(&sequence0, 0, Some(true));
        idxr.set_index(&sequence1, 1, Some(true)); 
        hps *= index_gen(&downsampled, idxr);
    }

    return log1p(&hps);
}

pub fn get_frequencies(spectrogram: Array) -> Array
{
    imax(&spectrogram, 0).1
}

pub fn to_host(spectrogram_af : Array) -> Spectrogram
{
    let window_size = spectrogram_af.dims()[0];
    let slice_len = window_size * spectrogram_af.dims()[1];
    let mut host = vec![0.; slice_len as usize];
    spectrogram_af.host::<f64>(host.as_mut_slice());

    let mut spectrogram : Spectrogram = Vec::new();
    for column in host.chunks(window_size as usize)
    {
        spectrogram.push(column.to_vec());
    }

    return spectrogram;
}