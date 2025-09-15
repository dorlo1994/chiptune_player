import numpy as np
import pyaudio as pa
from numpy import ndarray, dtype

from music_utils import Note
from typing import Callable, NamedTuple, Any


# Waveforms
def sin(t: np.ndarray[float]) -> ndarray[tuple[Any, ...], dtype[Any]]:
    """
    Sine wave
    """
    return np.sin(t)


def square(t: np.ndarray[float]) -> ndarray[tuple[Any, ...], dtype[Any]]:
    """
    Square wave going directly from 1 to -1 and back.
    """
    return np.where(np.sin(t) > 0, 1.0, -1.0)


def sawtooth(t: np.ndarray[float]) -> ndarray[tuple[Any, ...], dtype[Any]]:
    """
    Sqwtooth shaped wave rising linearly from -1 to 1 and wraps
    back to -1
    """
    return ((t % np.pi) / np.pi - 0.5) * 2


def triangle(t: np.ndarray[float]) -> ndarray[tuple[Any, ...], dtype[Any]]:
    """
    Triangle wave going linearly between 1 and -1
    """
    up_t = ((2 * (t - np.pi / 2)) % (2 * np.pi)) / np.pi - 1
    down_t = ((-2 * (t - np.pi / 2)) % (2 * np.pi)) / np.pi - 1
    return np.where(0 < np.cos(t), up_t, down_t)

Waveform = Callable[[np.ndarray[float]], ndarray[tuple[Any, ...], dtype[Any]]]

class PlayingNote(NamedTuple):
    note: np.float64
    waveform: str


class NotePlayer:
    """
    Holds a PyAudio object and manages how notes are played
    continuously.
    """
    WAVE_GENERATORS: dict[str: Waveform] = {
        'sin': sin,
        'square': square,
        'sawtooth': sawtooth,
        'triangle': triangle
    }

    def __init__(self, sample_freq: int, buffer_size: float):
        self._sample_freq: int = sample_freq
        self._buffer_size: int = int(buffer_size * sample_freq)
        self._player: pa.PyAudio = pa.PyAudio()
        self._stream = self._player.open(format=pa.paFloat32,
                                         channels=1,
                                         rate=self._sample_freq,
                                         output=True)
        self._notes_queue: dict[PlayingNote: tuple[list[float], float]] = dict()
        self._base_func: np.ndarray[dtype: np.float32] = 2 * np.pi * np.arange(self._buffer_size)

    def __del__(self):
        if self.__getattribute__("_stream"):
            self._stream.stop_stream()
            self._stream.close()
            self._player.terminate()

    def _add_note_to_queue(self, note: Note, waveform: str, new_queue: dict[PlayingNote: tuple[float, float]]):
        """
        Inserts a note into the queue to be played, and ensures continuity.
        """
        found_note = False
        for playing_note in self._notes_queue.keys():
            if playing_note.note == note.freq and playing_note.waveform == waveform:
                new_queue[playing_note] = (self._notes_queue[playing_note][0][-1] + self._base_func * playing_note.note / self._sample_freq,
                                           (self._notes_queue[playing_note][1] + 1) / 2)
                found_note = True
                break
        if not found_note:
            key = PlayingNote(note.freq, waveform)
            new_queue[key] = (self._base_func * note.freq / self._sample_freq, 0.1)

    def set_notes(self, notes: list[Note], waveforms: list[str]):
        """
        Prepare queue of notes to be played.
        """
        new_queue: dict[PlayingNote: tuple[list[float], float]] = dict()
        for note, waveform in zip(notes, waveforms):
            self._add_note_to_queue(note, waveform, new_queue)
        self._notes_queue = new_queue

    def play(self):
        """
        Calculate waveforms for currently playing note and write to
        the buffer to play them.
        """
        component_waves: list[np.ndarray[dtype[np.float32]]] = []
        playing_note: PlayingNote
        note_data: tuple[np.ndarray[float], float]

        for playing_note, note_data in self._notes_queue.items():
            wave_gen: Waveform = self.WAVE_GENERATORS[playing_note.waveform]
            wave: np.ndarray[tuple[Any, ...], dtype[Any]] = wave_gen(note_data[0]) * note_data[1]
            component_waves.append(wave.astype(np.float32))
        if component_waves:
            wave = np.sum(component_waves, axis=0) / len(component_waves)
        else:
            wave = np.zeros(self._buffer_size, dtype=np.float32)

        output_bytes = wave.tobytes()
        self._stream.write(output_bytes)
