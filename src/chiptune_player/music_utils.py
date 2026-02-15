from __future__ import annotations

import numpy as np
import re

from enum import auto, Enum
from numpy import ndarray, dtype
from typing import Callable, NamedTuple, Any, Self


def flat(delta: int) -> int:
    """
    Lower a delta without octaves by one semitone.
    """
    return (delta - 1) % 12


def sharp(delta: int) -> int:
    """
    Raise a delta without octaves by one semitone.
    """
    return (delta + 1) % 12


# These dicts match each note on the scale to the delta from A.
NAT_DELTAS: dict[str: int] = {'A': 0, 'B': 2, 'C': 3, 'D': 5, 'E': 7, 'F': 8, 'G': 10}
FLAT_DELTAS: dict[str: int] = {f'{note}b': flat(delta) for note, delta in NAT_DELTAS.items()}
SHARP_DELTAS: dict[str: int] = {f'{note}#': sharp(delta) for note, delta in NAT_DELTAS.items()}
DELTAS: dict[str: int] = {**NAT_DELTAS, **FLAT_DELTAS, **SHARP_DELTAS}

# This dict is the inverse of DELTAS, matches deltas from A to lists of their
# corresponding notes.
FROM_DELTAS: dict[int: list[str]] = {delta: [note for note in DELTAS.keys() if DELTAS[note] == delta] for delta in DELTAS.values()}


class Interval:
    """
    This class represents an interval between notes, such as an
    octave or a fifth.
    """
    SEMITONE_FACTOR: float = np.power(2, 1/12)

    def __init__(self, semitones: int, octaves: int):
        self.semitones = semitones + 12 * octaves
        self.factor = np.power(self.SEMITONE_FACTOR, self.semitones)

    def __add__(self, other: Self) -> Self:
        """
        Adding two intervals creates a new interval that corresponds
        to applying both.
        """
        assert isinstance(other, Interval)
        semitone_interval = self.semitones + other.semitones
        return Interval(semitone_interval % 12, semitone_interval // 12)

    def __sub__(self, other: Self) -> Self:
        assert isinstance(other, Interval)
        semitone_interval = self.semitones - other.semitones
        return Interval(semitone_interval % 12, semitone_interval // 12)

    def __repr__(self):
        return f'I({self.semitones})'

    @staticmethod
    def from_delta(delta: int) -> Interval:
        """
        Returns an Interval object from single number of semitones.
        """
        octaves = delta // 12
        semitones = delta - 12 * octaves
        return Interval(semitones, octaves)


class Note:
    """
    This class holds represents a Note on the piano,
    calculates the frequency corresponding to it
    """
    BASE_FREQUENCY = 55.0  # Frequency of A1
    NAME_PATTERN = r'(?P<Note>[A-G](?:#|b)?)(?P<Octave>\d+)'

    def __init__(self, name: str):
        self._note, self._octave = re.match(self.NAME_PATTERN, name).groups()
        self._octave = int(self._octave)
        semitone_delta = DELTAS[self._note]
        octave_delta = self._octave - 1
        interval = Interval(semitone_delta, octave_delta)
        self.freq = self.BASE_FREQUENCY * interval.factor

    @property
    def delta(self) -> int:
        return 12 * self._octave + DELTAS[self._note]

    def __sub__(self, other: Self) -> Interval:
        """
        Difference between notes is an interval
        """
        if isinstance(other, Note):
            delta = self.delta - other.delta
            return Interval.from_delta(delta)
        else:
            raise ValueError(f"Subtraction unsupported for Note with type {type(other)}.")

    def __mul__(self, other: Interval) -> Self:
        """
        Interval applied to note is a new note shifted by
        that interval.
        """
        if isinstance(other, Interval):
            delta = self.delta + other.semitones
            semitone_delta = delta % 12
            note = FROM_DELTAS[semitone_delta][0]
            octave = delta // 12
            name = f'{note}{octave}'
            return Note(name)
        else:
            raise ValueError(f"Multiplication unsupported for Note with type {type(other)}.")

    def __repr__(self):
        return f'{self._note}{self._octave}'

    def __eq__(self, other):
        return self.delta == other.delta


# Consts to calculate major and minor chords
MAJOR_THIRD = Note('E4') - Note('C4')
MINOR_THIRD = Note('G4') - Note('E4')
FIFTH = MAJOR_THIRD + MINOR_THIRD


def major(note):
    """
    Creates a major chord with the given note as the base.
    Returns a list of notes.
    """
    if isinstance(note, str):
        note = Note(note)
    return [note,
            note * MAJOR_THIRD,
            note * FIFTH]


def minor(note):
    """
    Creates a minor chord with the given note as the base.
    Returns a list of notes.
    """
    if isinstance(note, str):
        note = Note(note)
    return [note,
            note * MINOR_THIRD,
            note * FIFTH]

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
    Sawtooth shaped wave rising linearly from -1 to 1 and wraps
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

class Wave(Enum):
    SIN = auto(), sin
    SQUARE = auto(), square
    SAWTOOTH = auto(), sawtooth
    TRIANGLE = auto(), triangle

    def __init__(self, value, waveform: Waveform):
        self._waveform = waveform

    def __call__(self, t: np.ndarray[float]) -> ndarray[tuple[Any, ...], dtype[Any]]:
        return self._waveform(t)

    def __repr__(self):
        return self._waveform.__name__

    def __str__(self):
        return self._waveform.__name__

    @classmethod
    def from_name(cls, name: str) -> Self:
        from_names = {str(member): member for member in cls}
        return from_names[name]

    @classmethod
    def name_pattern(cls) -> str:
        return f'(?P<Waveform>{'|'.join([str(member) for member in cls])})'
