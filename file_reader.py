import re

from music_utils import Note
from player import Wave
from typing import NamedTuple

class ReadNote(NamedTuple):
    note: Note
    beats: float
    wave: Wave

class NoteSheet:
    DURATION_PATTERN = r'(?P<duration>\d+(?:\.\d+)?)'
    READ_NOTE_PATTERN = fr'{Note.NAME_PATTERN}-{Wave.name_pattern()}-{DURATION_PATTERN}'
    def __init__(self, bpm: int):
        self._bpm: int = bpm
        self._sheet: list[list[ReadNote]] | None = None

    @property
    def beat_length(self) -> float:
        return 60.0 / self._bpm

    def set_notes(self, notes: list[list[str]]):
        self._sheet = list()
        last_index = 0
        for beat in notes:
            notes_in_beat = list()
            beat_index = int(beat.pop(0))
            self._sheet[last_index:beat_index] = list()
            last_index = beat_index
            for read_note_str in beat:
                note_name, note_octave, wave, duration = re.match(self.READ_NOTE_PATTERN, read_note_str).groups()
                note = Note(f'{note_name}{note_octave}')
                wave = Wave.from_name(wave)
                duration = float(duration)
                read_note = ReadNote(note, duration, wave)
                notes_in_beat.append(read_note)
            self._sheet.append(notes_in_beat)

    def read_notes(self):
        if not self._sheet:
            raise Exception('Notes unset!')
        for line in self._sheet:
            print([str(note) for note in line])


class CustomFileReader:
    def __init__(self, filename, mode="r", encoding="utf-8"):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None

    def __enter__(self):
        # Open the file when entering context
        self.file = open(self.filename, self.mode, encoding=self.encoding)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Ensure file is closed even if an error occurs
        if self.file:
            self.file.close()
        # Returning False will re-raise any exception that occurred
        return False

    def read(self):
        """Read the entire file content."""
        if self.file:
            return self.file.read()
        raise ValueError("File is not open.")

    def readline(self):
        """Read a single line from the file."""
        if self.file:
            return self.file.readline()
        raise ValueError("File is not open.")

    def readlines(self):
        """Read all lines as a list."""
        if self.file:
            return self.file.readlines()
        raise ValueError("File is not open.")
