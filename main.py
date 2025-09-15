from music_utils import major, minor, Note
from player import NotePlayer


def main():
    subdivision = 100
    player = NotePlayer(44100, 1.2 / subdivision)
    while True:
        try:
            notes = major('A4')
            player.set_notes(notes, ['sawtooth' for _ in notes])
            player.play()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
