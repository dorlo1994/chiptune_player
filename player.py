import numpy as np
import pyaudio as pa
from numpy import dtype
from typing import NamedTuple, Any

from file_reader import NoteSheet, ReadNote
from music_utils import Note, Wave, Waveform

class Sound(NamedTuple):
    note: np.float64
    waveform: Wave

class PlayingNote:
    def __init__(self, sound: Sound, duration_in_seconds: float):
        self.sound = sound
        self._duration = duration_in_seconds
        self._remaining_duration = self._duration
        self._buffer_time: float = 0.0

    def decrease_duration(self, decrease: float):
        if self.alive:
            self._remaining_duration -= decrease

    @property
    def alive(self):
        return self._remaining_duration > 0

    def __str__(self):
        return f'Playing Note playing sound {self.sound} for {self._duration} seconds, of which {self._remaining_duration} remain!'

class NotePlayer:
    """
    Holds a PyAudio object and manages how notes are played
    continuously.
    """
    def __init__(self, sample_freq: int, buffer_size: float):
        self._sample_freq: int = sample_freq
        self._buffer_size: int = int(buffer_size * sample_freq)
        self._buffer_time = self._buffer_size / sample_freq
        self._player: pa.PyAudio = pa.PyAudio()
        self._stream = self._player.open(format=pa.paFloat32,
                                         channels=1,
                                         rate=self._sample_freq,
                                         output=True)
        self._notes_queue: dict[Sound: tuple[list[float], float]] = dict()
        self._base_func: np.ndarray[dtype: np.float32] = 2 * np.pi * np.arange(self._buffer_size)

    def __del__(self):
        if self.__getattribute__("_stream"):
            self._stream.stop_stream()
            self._stream.close()
            self._player.terminate()

    def _add_note_to_queue(self, note: Note, waveform: Wave, new_queue: dict[Sound: tuple[float, float]]):
        """
        Inserts a note into the queue to be played, and ensures continuity.
        """
        found_note = False
        for sound in self._notes_queue.keys():
            if sound.note == note.freq and sound.waveform == waveform:
                new_queue[sound] = (self._notes_queue[sound][0][-1] + self._base_func * sound.note / self._sample_freq,
                                           (self._notes_queue[sound][1] + 1) / 2)
                found_note = True
                break
        if not found_note:
            key = Sound(note.freq, waveform)
            new_queue[key] = (self._base_func * note.freq / self._sample_freq, 0.1)

    def set_notes(self, notes: list[Note], waveforms: list[Wave]):
        """
        Prepare queue of notes to be played.
        """
        new_queue: dict[Sound: tuple[list[float], float]] = dict()
        for note, waveform in zip(notes, waveforms):
            self._add_note_to_queue(note, waveform, new_queue)
        self._notes_queue = new_queue

    def _add_sound_to_queue(self, sound: Sound, new_queue: dict[Sound: tuple[float, float]]):
        """
        Inserts a sound into the queue to be played, and ensures continuity.
        """
        found_note = False
        for current_sound in self._notes_queue.keys():
            if sound.note == current_sound.note and sound.waveform == current_sound.waveform:
                new_queue[current_sound] = (self._notes_queue[current_sound][0][-1] + self._base_func * sound.note / self._sample_freq,
                                           (self._notes_queue[current_sound][1] + 1) / 2)
                found_note = True
                break
        if not found_note:
            new_queue[sound] = (self._base_func * sound.note / self._sample_freq, 0.1)

    def set_sounds(self, sounds: list[Sound]):
        """
        Prepare sound of notes to be played.
        """
        new_queue: dict[Sound: tuple[list[float], float]] = dict()
        for sound in sounds:
            self._add_sound_to_queue(sound, new_queue)
        self._notes_queue = new_queue

    def process_notes(self, notes_to_play: list[ReadNote], beat_time: float, current_notes) -> list[PlayingNote]:
        for note_to_play in notes_to_play:
            note_as_sound: Sound = Sound(note_to_play.note.freq, note_to_play.wave)
            if note_as_sound not in [read_note.sound for read_note in current_notes]:
                duration = note_to_play.beats * beat_time
                new_playing_note: PlayingNote = PlayingNote(sound=note_as_sound,
                                                            duration_in_seconds=duration
                                                            )
                current_notes.append(new_playing_note)
        current_notes = [note for note in current_notes if note.alive]
        for note in current_notes:
            note.decrease_duration(self._buffer_time)
        return current_notes

    def play_from_sheet_music(self, note_sheet: NoteSheet):
        beat_time = note_sheet.beat_time
        play_time = note_sheet.play_time
        total_samples = self._sample_freq * play_time
        num_buffers = int(total_samples / self._buffer_size)
        self._buffer_time = self._buffer_size / self._sample_freq
        current_time = 0.0
        current_beat: int = 0

        current_notes: list[PlayingNote] = list()
        all_notes: list[list[ReadNote]] = note_sheet.get_notes()
        buffers: list[bytes] = list()
        for buffer in range(num_buffers):
            if current_beat > len(all_notes):
                break
            notes_to_play: list[ReadNote] = all_notes[min(current_beat, len(all_notes)- 1)]
            current_notes = self.process_notes(notes_to_play, beat_time, current_notes)
            current_notes_as_sounds = [note.sound for note in current_notes]
            self.set_sounds(current_notes_as_sounds)
            new_buffer: bytes = self.export_buffer()
            buffers.append(new_buffer)
            current_time += self._buffer_time
            current_beat = int(current_time / beat_time)

        self.play_buffers(buffers)

    def export_buffer(self) -> bytes:
        component_waves: list[np.ndarray[dtype[np.float32]]] = []
        sound: Sound
        note_data: tuple[np.ndarray[float], float]

        for sound, note_data in self._notes_queue.items():
            wave_gen: Waveform = sound.waveform
            wave: np.ndarray[tuple[Any, ...], dtype[Any]] = wave_gen(note_data[0]) * note_data[1]
            component_waves.append(wave.astype(np.float32))
        if component_waves:
            wave = np.sum(component_waves, axis=0) / len(component_waves)
        else:
            wave = np.zeros(self._buffer_size, dtype=np.float32)

        return wave.tobytes()

    def play_buffers(self, buffers: list[bytes]):
        for buffer in buffers:
            self._stream.write(buffer)

    def play(self):
        """
        Calculate waveforms for currently playing note and write to
        the buffer to play them.
        """
        output_bytes = self.export_buffer()
        self._stream.write(output_bytes)
