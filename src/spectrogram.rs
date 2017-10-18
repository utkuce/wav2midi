extern crate num_cpus;

extern crate apodize;
extern crate itertools_num;

use arrayfire::*;
use self::apodize::{hanning_iter};
use self::itertools_num::linspace;
use std::{f64, thread};

type Column = Vec<::std::os::raw::c_double>;
type Spectrogram = Vec<Column>;

pub fn get_spectrogram(audio_data : Array, window_size: usize, step_size: usize) -> Vec<Array>
{
    let mut spectrogram_af : Vec<Array> = Vec::new();
    let audio_len : usize = audio_data.dims()[0] as usize;

    let cpu_count = num_cpus::get();
    let mut thread_handles : Vec<thread::JoinHandle<(usize, Vec<Array>)>> = Vec::new();    
    let mut chunk_size = (audio_len as f32 / cpu_count as f32).ceil() as usize;

    for part_number in 0..cpu_count
    {
        let mut start = part_number*chunk_size;

        if part_number > 0 { start -= window_size-step_size;  }
        if start + chunk_size > audio_len { chunk_size -= start + chunk_size - audio_len; }

        let sequence =  Seq::new(start as u32, (start+chunk_size) as u32, 1);
        let mut idxr = Indexer::new();                
        idxr.set_index(&sequence, 0, Some(false));
        let part = index_gen(&audio_data, idxr);

        let handle : thread::JoinHandle<(usize, Vec<Array>)> = thread::spawn(move || 
        {
            let mut part_result : Vec<Array> = Vec::new();
            let part_len : usize = part.dims()[0] as usize;
            for index in (0..part_len-window_size).step_by(step_size)
            {
                let sequence =  Seq::new(index as u32, (index as u32) + (window_size) as u32, 1);
                let mut idxr = Indexer::new();                
                idxr.set_index(&sequence, 0, Some(false));
                let values = index_gen(&part, idxr);

                let dim = values.dims();
                let hanning = Array::new(&hanning_iter(dim[0] as usize).collect::<Vec<f64>>(), dim);
                
                let input = values * hanning;
                let output : Array = fft(&input, 1.0, window_size as i64);
                part_result.push(decomplexify(output));
            }

            return (part_number, part_result);
        });

        thread_handles.push(handle);  
    }

    let mut results_in_order = vec![Vec::new(); cpu_count];
    for handle in thread_handles 
    {
        let tuple : (usize, Vec<Array>) = handle.join().unwrap(); 
        results_in_order[tuple.0] = tuple.1;
    }

    for result in &mut results_in_order { spectrogram_af.append(result); }

    return spectrogram_af;
}

fn decomplexify(array : Array) -> Array
{
    let sequence =  Seq::new(0 as u32, ((array.dims()[0] as f32 / 2.).floor()-1.) as u32, 1);
    let mut idxr = Indexer::new();            
    idxr.set_index(&sequence, 0, Some(false));
    let half = index_gen(&array, idxr);

    let magnitude = sqrt( &(pow(&real(&half),&2, true) * pow(&imag(&half),&2, true)) );
    floor(&log1p(&magnitude))
}

fn resample(array: Array, new_length : usize)
{
    
}

pub fn combine(narrowband : Vec<Array>, wideband : Vec<Array>) -> Vec<Array>
{
    let mut combined : Vec<Array> = Vec::new();
    let scale = wideband.len() as f32 / narrowband.len() as f32;

    for (index, column) in narrowband.iter().enumerate()
    {
        let pos : Vec<f64> = linspace::<f64>(0., column.dims()[0] as f64, wideband[0].dims()[0] as usize).collect();
        let pos_af = Array::new(&pos, Dim4::new(&[wideband[0].dims()[0], 1,1,1]));       
        let column_interp = approx1(column, &pos_af , InterpType::NEAREST, 0.0);
        let mut i = (index as f32 * scale).round() as usize;
        if i == wideband.len() { i -= 1; }
        combined.push(column_interp * wideband[i].clone());
    }

    return combined;
}

pub fn to_host(spectrogram_af : Vec<Array>) -> Spectrogram
{
    let cpu_count = num_cpus::get();
    let mut thread_handles : Vec<thread::JoinHandle<(usize, Spectrogram)>> = Vec::new();    
    let chunk_size = (spectrogram_af.len() as f32 / cpu_count as f32).ceil() as usize;

    for (index, piece) in spectrogram_af.chunks(chunk_size).enumerate()
    {  
        let owned_piece : Vec<Array> = Vec::from(piece);
        let handle : thread::JoinHandle<(usize, Spectrogram)> = thread::spawn(move || 
        {
            let mut sub_spect : Spectrogram = Vec::new();
            for column_af in owned_piece
            {
                let mut v = vec![0.; column_af.elements()];
                let slice : &mut [f64] = v.as_mut_slice();
                column_af.host(slice);
                sub_spect.push(slice.to_vec());
            }

            return (index, sub_spect);
        });

        thread_handles.push(handle);         
    }

    let mut sub_spects : Vec<Spectrogram> = vec![Vec::new(); cpu_count];

    for handle in thread_handles 
    {
        let tuple : (usize, Spectrogram) = handle.join().unwrap(); 
        sub_spects[tuple.0] = tuple.1;
    }

    let mut final_spectrogram : Spectrogram = Vec::new();
    for part in sub_spects.iter() {
        let mut part = part.clone();
        final_spectrogram.append(&mut part);
    }

    return final_spectrogram;
}