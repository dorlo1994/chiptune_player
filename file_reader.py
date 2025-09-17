import re

from music_utils import Note, Wave, Wave, Wave, Wave
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
    def beat_time(self) -> float:
        return 60.0 / self._bpm

    @property
    def play_time(self) -> float:
        if not self._sheet:
            return 0.0
        return (len(self._sheet) + max([note.beats for note in self._sheet[-1]])) * self.beat_time

    def set_notes(self, notes: list[list[str]]):
        """
        Get a list of notes, each of which contains an index of the beat for the note, and
        a list of notes to play. Initializes the list of beats and each note played in them.
        """
        self._sheet = list()
        last_index = 0
        for beat in notes:
            beat_index = int(beat.pop(0))
            while last_index < beat_index:
                self._sheet.append(list())
                last_index += 1
            notes_in_beat = list()
            for read_note_str in beat:
                note_name, note_octave, wave, duration = re.match(self.READ_NOTE_PATTERN, read_note_str).groups()
                note = Note(f'{note_name}{note_octave}')
                wave = Wave.from_name(wave)
                duration = float(duration)
                read_note = ReadNote(note, duration, wave)
                notes_in_beat.append(read_note)
            self._sheet.append(notes_in_beat)

    def __str__(self):
        if not self._sheet:
            return 'No notes.'
        return_str = ''
        for beat, line in enumerate(self._sheet):
            return_str += ''.join([f'{beat}: ', *[str(note) for note in line], '\n'])
        return return_str

    def get_notes(self) -> list[list[ReadNote]]:
        return self._sheet


class MusicFileReader:
    def __init__(self, filename, mode="r", encoding="utf-8"):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None
        self._note_sheet: NoteSheet | None = None

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

    def read_notes(self):
        """
        Read all lines as list of notes and initializes the note sheet
        """
        if not self.file:
            raise ValueError("File is not open.")

        notes: list[list[str]] = []
        for line in self.file.readlines():
           if not self._note_sheet:
               self._note_sheet = NoteSheet(bpm=int(line))
               continue

           notes_in_line: list[str] = line.split(' ')
           notes.append(notes_in_line)
        self._note_sheet.set_notes(notes=notes)
        return self._note_sheet