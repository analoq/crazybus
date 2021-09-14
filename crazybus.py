from math import log2
from random import randrange
from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo

MEASURES = 32
TICKS_PER_BEAT = 120

def pitch_to_hz(pitch : int) -> float:
    return 3579545 / (32 * (1024 - pitch))

def hz_to_note(frequency : float) -> float:
    return 12*log2(frequency/440.0) + 69

def random_pitch(offset : int) -> int:
    return (randrange(40)*10 + offset) % 0x3ff

def bend_for_note(note : float) -> int:
    return round((note - int(note))*4096)

if __name__ == "__main__":
    assert(hz_to_note(880.0) == 69+12)
    assert(hz_to_note(440.0) == 69+0)
    assert(hz_to_note(220.0) == 69-12)
    assert(bend_for_note(60.5) == 2048)

    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    tempo_track = MidiTrack()
    tempo_track.append(MetaMessage('set_tempo', time=0, tempo=bpm2tempo(90)))
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

            mid.tracks[track_num].append(
                Message('pitchwheel', time=0, channel=track_num, pitch=bend))
            mid.tracks[track_num].append(
                Message('note_on', time=0, channel=track_num, note=note_floor, velocity=64))
            mid.tracks[track_num].append(
                Message('note_off', time=TICKS_PER_BEAT//4, channel=track_num, note=note_floor, velocity=127))

    mid.save('output.mid')
