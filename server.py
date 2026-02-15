from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.post("/render")
def render():
    data = generate_wave()
    wav_bytes = render_wav_bytes(data)

    return Response(
        content=wav_bytes,
        media_type="audio/wav"
    )

@app.get("/health")
def health():
    return {"status": "ok"}
