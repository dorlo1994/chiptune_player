# 🎵 Chiptune Player

A lightweight **Python-based chiptune player** that reads and plays retro-style music files.
Built as a personal project to explore audio file parsing, playback, and modular workflow design.

_Last updated: 2025-10-21_

---

## 🧠 Overview

This project demonstrates:

- How to **read and interpret chiptune file formats**
- Building a **modular workflow** for audio playback
- Using Python for low-level data handling and simple music synthesis

Core modules:

- `file_reader.py` – parses chiptune files  
- `music_utils.py` – helper functions for timing, frequencies, and transforms  
- `player.py` – handles playback logic  
- `main.py` – entry point for running the player

---

## ⚙️ Installation

1. Clone this repository:

```bash
git clone https://github.com/dorlo1994/chiptune_player.git
cd chiptune_player
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the player with a chiptune file path:

```bash
python main.py <path_to_music_file>
```

Example:

```bash
python main.py demo_song.chip
```

If the project includes demo assets, you can run the bundled demo:

```bash
python main.py demo/demo_song.chip
```

If your player requires an audio backend (e.g., `pygame`), ensure it’s installed and configured for your platform.

---

## 📁 Project Structure

```
chiptune_player/
│
├── file_reader.py
├── music_utils.py
├── player.py
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🧩 Design & Architecture

The codebase follows a simple pipeline pattern:

1. **Ingest** — `file_reader.py` reads and parses raw chiptune data into structured events.  
2. **Transform** — `music_utils.py` converts events into timing/frequency data and helper primitives.  
3. **Execute** — `player.py` schedules and plays the produced audio frames (or delegates to an audio backend).  
4. **Orchestrate** — `main.py` wires the modules together and handles CLI input.

This separation keeps modules focused, testable, and easy to iterate on.

---

## 🛠️ Development Notes

- Add docstrings and inline comments when extending functionality.  
- Keep `file_reader` format parsing isolated from playback code to enable support for multiple file formats.  
- Consider using `pygame`, `sounddevice`, or similar libraries for cross-platform audio output.  
- If using binary chiptune formats, treat parsing carefully and include defensive error handling.

---

## 📁 Demo & Assets

If including demo files or audio samples, place them under `demo/` or `assets/` and reference them in usage examples. Provide small sample files or links to audio previews when possible.

---

## 🧩 Roadmap

- [ ] Add support for additional chiptune file formats  
- [ ] Implement waveform visualization (CLI or simple GUI)  
- [ ] Add unit and integration tests for core modules  
- [ ] Improve error handling and input validation  
- [ ] Package for distribution (PyPI) if a stable API is defined

---

## 🧑‍💻 Author

**dorlo1994**  
Workflow Architect | DevOps / MLOps Engineer  
Exploring structure, automation, and learning through creative projects.

---

## 🪪 License

This project is available under the MIT License — see [LICENSE](LICENSE) for details.
