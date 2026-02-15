from chiptune_player.player import NotePlayer
from chiptune_player.file_reader import parse_lines, NoteSheet

from fastapi import FastAPI, Body
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware


subdivision = 1000.0

app = FastAPI()
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/render")
def render(notes_text: str = Body(..., media_type="text/plain")):
    lines = [line.split() for line in notes_text.strip().splitlines()]
    note_sheet: NoteSheet = parse_lines(lines)
    player = NotePlayer(44100, 1.2 / subdivision)
    wav_bytes = player.render_from_sheet(note_sheet)

    return Response(
        content=wav_bytes,
        media_type="audio/wav"
    )

@app.get("/health")
def health():
    return {"status": "ok"}
