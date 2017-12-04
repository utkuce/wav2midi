extern crate rimd;

use std::{f64, fmt};
use self::rimd::{ TrackEvent, Event, MidiMessage, SMFWriter, SMFFormat, Track, SMF};
use std::path::Path;
use std::collections::HashMap;

pub struct Note {name: String, midi: u8, duration: u64}
pub struct Song{pub notes: Vec<Note>, pub division: i16, pub name: String}

impl fmt::Display for Song {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let all_notes : String = 
            self.notes.iter().fold(String::new(), |s, n| 
                format!("{}{}", s, format!("{}[{}] ", n.name, n.duration)));
        write!(f, "{}: {}", self.name, all_notes)
    }
}

fn get_pitch(frequency : u32) -> (String, u8) 
{
    if frequency < 16 { return (String::from("R"), 0); }

    let notes = vec![ "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B" ];
    
    //distance to A440 of the note
    let log_base : f64 = (2.0 as f64).powf(1.0/12.0);   
    let mut offset : i32 = ((frequency as f64 / 440.0).log(log_base)).round() as i32;

    let midi = 69 + offset; // A4 in midi is 69
    
    //adjust offset for the array
    offset += if offset >= 0 {9} else {-2}; 
    let note_index : usize = if offset >= 0 {offset%12} else {11 + offset%12} as usize;
    return (format!( "{note}{octave}", note = notes[note_index], octave = 4 + offset/12), midi as u8);
}

pub fn get_notes(frequencies: &[u32], onsets: &[f64], no_onset: bool) -> Vec<Note>
{
    let vec : Vec<(String, u8)> = frequencies.iter().map(|freq| get_pitch(*freq)).collect();
    let mut notes : Vec<Note> = Vec::new();

    if no_onset
    {
        let mut last: usize = 0;
        for i in 1..vec.len()
        {
            if vec[i] != vec[i-1] || i == vec.len()-1 {
                notes.push( Note { 
                    name: vec[i-1].0.clone(), midi: vec[i-1].1.clone(), 
                    duration: (i-last) as u64 
                } );
                last = i;
            }
        }
    }
    else
    {
        let mut onsets_clone : Vec<f64> = onsets.clone().to_vec();
        onsets_clone.push(1.);
        let mut previous_onset : f64 = 0.;
        for &onset in &onsets_clone
        {
            let start_index : usize = (frequencies.len() as f64 * previous_onset).round() as usize;
            let end_index : usize = (frequencies.len() as f64 * onset).round() as usize;

            let interval : &[(String,u8)] = &vec[start_index..end_index];

            let mode = mode(interval);
            let duration : u64 = end_index as u64 - start_index as u64;

            notes.push( Note {
                name: mode.0.clone(), midi: mode.1.clone(),  duration: duration
            });

            previous_onset = onset;
        }
    }


    return notes;
}

fn mode(elements: &[(String,u8)]) -> &(String,u8) {

    let mut occurrences = HashMap::new();

    for value in elements {
        *occurrences.entry(value).or_insert(0) += 1;
    }

    occurrences.into_iter()
        .max_by_key(|&(_, count)| count)
        .map(|(val, _)| val)
        .expect("Cannot compute the mode of zero elements")
}

pub fn write_midi(song: Song) -> String
{   
    let mut midi_filename = song.name.clone();
    let mut events : Vec<TrackEvent> = Vec::new();

    let mut previous_duration = 0;
    for note in song.notes.iter() 
    {
        if note.name != "R" 
        {
            events.push( TrackEvent { 
                event: Event::Midi(MidiMessage::note_on(note.midi, 125, 0)), 
                vtime: previous_duration
            } );
        
            events.push( TrackEvent { 
                event: Event::Midi(MidiMessage::note_off(note.midi, 125, 0)), 
                vtime: note.duration 
            } );
        }

        if note.name == "R" { 
            previous_duration += note.duration;
        } else {
            previous_duration = note.duration as u64;
        }

    }

    let tracks = vec![ Track {copyright: None, name: None, events: events} ];
    let smf = SMF {format: SMFFormat::Single, tracks: tracks, division: song.division};
    let writer = SMFWriter::from_smf(smf);
 
    let result = writer.write_to_file(Path::new(format!("{}{}", song.name,".mid").as_str()));
    if result.is_err()
    {
        let song_ = Song {notes: song.notes, name: song.name+"_", division: song.division};
        midi_filename = write_midi(song_);
    }

    return midi_filename;
}