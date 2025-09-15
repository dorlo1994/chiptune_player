from music_utils import major, minor, Note
from player import NotePlayer


def main():
    subdivision = 100
    player = NotePlayer(44100, 1.2 / subdivision)
    notefile = 'notes.txt'
    # notes = [Note(n) for n in lines[-1].split(',')]
    try:
        notes = []
        player.set_notes(notes, ['triangle' for _ in notes])
        player.play()
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main()
