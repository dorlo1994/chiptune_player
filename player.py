from collections import namedtuple

import numpy as np
import pyaudio as pa


# Waveforms
def sin(t):
    """
    Sine wave
    """
    return np.sin(t)


def square(t):
    """
    Square wave going directly from 1 to -1 and back.
    """
    return np.where(np.sin(t) > 0, 1, 0)


def sawtooth(t):
    """
    Sqwtooth shaped wave rising linearly from -1 to 1 and wraps
    back to -1
    """
    return ((t % np.pi) / np.pi - 0.5) * 2


def triangle(t):
    """
    Triangle wave going linearly between 1 and -1
    """
    up_t = ((2 * (t - np.pi / 2)) % (2 * np.pi)) / np.pi - 1
    down_t = ((-2 * (t - np.pi / 2)) % (2 * np.pi)) / np.pi - 1
    return np.where(np.cos(t) > 0, up_t, down_t)


PlayingNote = namedtuple('PlayingNote', ['note', 'waveform'])


class NotePlayer:
    """
    Holds a PyAudio object and manages how notes are played
    continuously.
    """
    WAVE_GENERATORS = {
        'sin': sin,
        'square': square,
        'sawtooth': sawtooth,
        'triangle': triangle
    }

    def __init__(self, sample_freq, buffer_size):
        self._sample_freq = sample_freq
        self._buffer_size = int(buffer_size * sample_freq)
        self._player = pa.PyAudio()
        self._stream = self._player.open(format=pa.paFloat32,
                                         channels=1,
                                         rate=self._sample_freq,
                                         output=True)
        self._notes_queue = dict()
        self._base_func = 2 * np.pi * np.arange(self._buffer_size)

    def __del__(self):
        if self.__getattribute__("_stream"):
            self._stream.stop_stream()
            self._stream.close()
            self._player.terminate()

    def _add_note_to_queue(self, note, waveform, new_queue):
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

    def set_notes(self, notes, waveforms):
        """
        Prepare queue of notes to be played.
        """
        new_queue = dict()
        for note, waveform in zip(notes, waveforms):
            self._add_note_to_queue(note, waveform, new_queue)
        self._notes_queue = new_queue

    def play(self):
        """
        Calculate waveforms for currently playing note and write to
        the buffer to play them.
        """
        component_waves = []

        for playing_note, note_data in self._notes_queue.items():
            wave_gen = self.WAVE_GENERATORS[playing_note.waveform]
            wave = wave_gen(note_data[0]) * note_data[1]
            component_waves.append(wave.astype(np.float32))
        if component_waves:
            wave = sum(component_waves) / len(component_waves)
        else:
            wave = np.zeros(self._buffer_size, dtype=np.float32)

        output_bytes = wave.tobytes()
        self._stream.write(output_bytes)
