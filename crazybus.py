"""Generate Crazybus music and save to MIDI file"""
from math import log2
from random import randrange
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo # type: ignore

MEASURES = 32
BPM = 90
TICKS_PER_BEAT = 120

def pitch_to_hz(pitch: int) -> float:
    """Convert 10-bit pitch to frequency in Hz"""
    return 3579545 / (32 * (1023 - pitch))

def hz_to_note(frequency: float) -> float:
    """Convert frequency in Hz to MIDI note number as float"""
    return 12*log2(frequency/440.0) + 69

def random_pitch(offset: int) -> int:
    """Generate a random 10-bit pitch given offset"""
    return (randrange(40)*10 + offset) % 0x3ff

def bend_for_note(note: float) -> int:
    """Determine the amount of pitch bend for a MIDI note number as float"""
    return round((note - int(note))*4096)

def test():
    """Test methods"""
    assert round(pitch_to_hz(440)) == 192
    assert hz_to_note(880.0) == 69+12
    assert hz_to_note(440.0) == 69+0
    assert hz_to_note(220.0) == 69-12
    assert bend_for_note(60.5) == 2048

def main():
    """Main program"""
    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', time=0, tempo=bpm2tempo(BPM)))
    mid.tracks.append(tempo_track)
    mid.tracks.append(MidiTrack())
    mid.tracks.append(MidiTrack())
    mid.tracks.append(MidiTrack())

    for _ in range(16*MEASURES):
        for track_num in range(1, 4):
            pitch = random_pitch(500 + 100*(track_num-1))
            freq = pitch_to_hz(pitch)
            note = hz_to_note(freq)
            bend = bend_for_note(note)
            note_floor = int(note) if note < 128 else 127

            pitchwheel = Message('pitchwheel',
                                 time=0,
                                 channel=track_num,
                                 pitch=bend)
            note_on = Message('note_on',
                              time=0,
                              channel=track_num,
                              note=note_floor,
                              velocity=64)
            note_off = Message('note_off',
                               time=TICKS_PER_BEAT//4,
                               channel=track_num,
                               note=note_floor,
                               velocity=127)
            mid.tracks[track_num].append(pitchwheel)
            mid.tracks[track_num].append(note_on)
            mid.tracks[track_num].append(note_off)

    mid.save('output.mid')

if __name__ == "__main__":
    test()
    main()
