from player import NotePlayer
from file_reader import MusicFileReader, NoteSheet


def main():
    subdivision = 1000.0
    note_filename = 'notes.txt'
    with MusicFileReader(note_filename) as reader:
        note_sheet: NoteSheet = reader.read_notes()
    player = NotePlayer(44100, 1.2 / subdivision)
    wav_data = player.render_from_sheet(note_sheet)
    with open('output.wav', 'wb') as f:
        f.write(wav_data.read())


if __name__ == "__main__":
    main()
