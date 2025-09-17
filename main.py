from player import NotePlayer
from file_reader import MusicFileReader, NoteSheet


def main():
    subdivision = 100
    note_filename = 'notes.txt'
    with MusicFileReader(note_filename) as reader:
        note_sheet: NoteSheet = reader.read_notes()
    player = NotePlayer(44100, 1.2 / subdivision)
    player.play_from_sheet_music(note_sheet)


if __name__ == "__main__":
    main()
