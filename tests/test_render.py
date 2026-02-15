import wave
import io

from chiptune_player.player import NotePlayer
from chiptune_player.file_reader import MusicFileReader

def test_render_generates_valid_wav():
    player = NotePlayer(44100, 0.1)
    with MusicFileReader("tests/sample.chip") as reader:
        note_sheet: NoteSheet = reader.read_notes()
    wav_bytes = player.render_from_sheet(note_sheet)

    assert isinstance(wav_bytes, bytes)
    assert len(wav_bytes) > 1000  # not empty

    buffer = io.BytesIO(wav_bytes)

    with wave.open(buffer, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 44100
        assert wf.getsampwidth() == 2

