from music_utils import major, minor, Note
from player import NotePlayer, Wave
from file_reader import NoteSheet


def main():
    subdivision = 100
    player = NotePlayer(44100, 1.2 / subdivision)
    note_sheet = NoteSheet(160)
    read_note_str = [['0', 'E4-sin-1']]
    note_sheet.set_notes(read_note_str)
    print(note_sheet.read_notes())
    while True:
        try:
            notes = [*minor('E4')]
            player.set_notes(notes, [Wave.TRIANGLE for _ in notes])
            player.play()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
