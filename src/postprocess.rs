use std::os::raw;
use std::f64;
use std::slice;
use std::fmt;

type Note = (String, usize); // pitch, duration
pub struct Song{notes: Vec<Note>}

impl fmt::Display for Song {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let all_notes : String = 
            self.notes.iter().fold(String::new(), |s, n| format!("{}{}", s, format!("{}[{}] ", n.0, n.1)));
        write!(f, "{}", all_notes)
    }
}

fn get_pitch<'a>(frequency : &'a f64) -> String {

    if frequency.round() as i32 == 0 { return String::from("R"); }

    let notes = vec![ "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B" ];
    
    //distance to A440 of the note
    let log_base : f64 = (2.0 as f64).powf(1.0/12.0);   
    let mut offset : i32 = ((frequency / 440.0).log(log_base)).round() as i32; 
    
    //adjust offset for the array
    offset += if offset >= 0 {9} else {-2}; 
    let note_index : usize = if offset >= 0 {offset%12} else {11 + offset%12} as usize;
    return format!( "{note}{octave}", note = notes[note_index], octave = 4 + offset/12);
}

pub fn get_song(frequencies: *const raw::c_double, len: raw::c_uint) -> Song
{
    let data: &[f64] = unsafe { slice::from_raw_parts(frequencies, len as usize) };
    let vec : Vec<String> = data.to_vec().iter().map(|freq| get_pitch(freq)).collect();

    let mut song = Song { notes: Vec::new() };

    let mut last: usize = 0;
    for i in 1..vec.len()
    {
        if vec[i] != vec[i-1] || i == vec.len()-1 {
            song.notes.push((vec[i-1].clone(), i-last));
            last = i;
        }
    }

    return song;
} 