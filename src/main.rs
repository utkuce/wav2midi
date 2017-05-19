extern crate hound;

fn main() {

    let fourier_window = 512;

    let mut reader = hound::WavReader::open("C:/Users/utku/Desktop/3_2.wav").unwrap();    
    let audio_data = reader.samples::<i16>().map( |sample| sample.unwrap() as f64);

    let mut fft_in : Vec<f64> = Vec::new();
    for (index, sample) in audio_data.enumerate() {
        fft_in.push(sample);
        if index % fourier_window == 0 {
            fft_in.clear();
            println!("{} {}", index, sample);
        }
    }
}