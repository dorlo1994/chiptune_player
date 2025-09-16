import numpy as np
import pyaudio as pa
from numpy import dtype
from typing import NamedTuple, Any

from file_reader import NoteSheet
from music_utils import Note, Wave, Waveform

class Sound(NamedTuple):
    note: np.float64
    waveform: Wave

class PlayingNote:
    def __init__(self, sound: Sound, duration_in_seconds: float):
        self._sound = sound
        self._duration = duration_in_seconds
        self._remaining_duration = self._duration

    def decrease_duration(self, decrease: float):
        if self.alive:
            self._remaining_duration -= decrease

    @property
    def alive(self):
        return self._remaining_duration > 0

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

    def play_from_sheet_music(self, note_sheet: NoteSheet):
        beat_time = note_sheet.beat_time
        play_time = note_sheet.play_time
        total_samples = self._sample_freq * play_time
        num_buffers = total_samples / self._buffer_size
        print(f'Number of available buffers: {num_buffers}')
        print(f'Number of buffers per beat: {num_buffers * (beat_time / play_time)}')


    def play(self):
        """
        Calculate waveforms for currently playing note and write to
        the buffer to play them.
        """
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

        output_bytes = wave.tobytes()
        self._stream.write(output_bytes)
