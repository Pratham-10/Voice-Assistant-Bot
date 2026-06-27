# Voice Assistant Bot 🎙️

A modernized, modular, and cross-platform desktop voice assistant written in Python. It supports speech-to-text input, system text-to-speech output, weather forecast checks, custom website launching, keyboard media controls, and AI-driven chat/generation features using the Google Gemini API.

## Features & Enhancements ✨

- **Cross-Platform Compatibility**: Fully compatible with macOS, Windows, and Linux.
  - *macOS*: Runs speech synthesis natively using the built-in `say` command (extremely fast, offline, and bypasses buggy `pyttsx3`/`pyobjc` builds on modern macOS).
  - *Windows*: Utilizes local SAPI5 synthesis via `pyttsx3` with an automated COM dispatch backup.
  - *Linux*: Falls back to `espeak` via `pyttsx3`.
- **Gemini API Integration**: Uses the official Google GenAI Python SDK (`google-genai`) with the `gemini-2.5-flash` model for super-fast, intelligent response times.
- **Environment Configurations**: Implemented standard `.env` configuration files for API keys instead of exposing them in python modules.
- **Fail-Safe Robustness**:
  - Automatically falls back to terminal keyboard input if a microphone is not found or `PyAudio` is not installed.
  - Wraps active application-level GUI keystrokes (`pyautogui`) to avoid accessibility permission crashes on macOS.
- **Modular Directory Structure**: Refactored the code from a single large script into clean, reusable modules.

---

## Directory Structure 📁

```
.
├── .env.example       # Environment configuration template
├── .gitignore         # File patterns to exclude from Git tracking
├── README.md          # User manual and setup documentation
├── requirements.txt   # Pip dependencies list
├── main.py            # Main runner file
└── src/
    ├── __init__.py    # Defines src as a package
    ├── config.py      # Dotenv configuration loading
    ├── tts.py         # Text-to-speech speak functions
    ├── stt.py         # Speech-to-text takeCommand functions
    ├── actions.py     # Weather, music play, and keyboard simulation actions
    └── ai.py          # Gemini AI chat and generation functions
```

---

## Installation & Setup 🚀

### 1. Install System Prerequisites

Depending on your Operating System, speech recognition may require installing system audio headers (`portaudio`).

- **macOS**:
  Install Xcode command line tools and Homebrew, then run:
  ```bash
  brew install portaudio
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get update
  sudo apt-get install portaudio19-dev python3-pyaudio espeak
  ```
- **Windows**:
  No system dependencies are usually required.

---

### 2. Configure Virtual Environment

It is recommended to run the project in a virtual environment to prevent polluting system packages.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS and Linux:
source .venv/bin/activate

# On Windows (cmd):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

Install the requirements using pip:

```bash
pip install -r requirements.txt
```

---

### 4. Environment Variables Setup

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your keys:
   - `GEMINI_API_KEY`: Get one from [Google AI Studio](https://aistudio.google.com/).
   - `WEATHER_API_KEY`: Get a free key from [OpenWeatherMap](https://openweathermap.org/api).
   - `MUSIC_PATH`: Absolute path to a local audio file (e.g. `/Users/username/Music/song.mp3` or `C:\Users\username\Music\song.mp3`).

---

## Usage 💻

Run the assistant from the root directory:

```bash
python main.py
```

### Voice Commands

- **Open Website**: Say `"Open Youtube"`, `"Open Google"`, `"Open Stackoverflow"`, or `"Open GeeksforGeeks"`.
- **Tell Time**: Say `"Time"` or `"What time is it"`.
- **Check Weather**: Say `"Weather in Mumbai"` or `"Weather in Jaipur"`. If you just say `"Weather"`, the assistant will prompt you for the city.
- **AI File Generation**: Say `"Using artificial intelligence write a python script to solve sudoku"` (requires `GEMINI_API_KEY`). This splits on `"intelligence"`, requests a code block, and saves the output as `Openai/write_a_python_script_to_solve_sudoku.txt`.
- **Enable Gemini Chat**: Say `"Enable chatting"`. You will enter a dedicated chatting mode. Say `"Quit chatting"` to exit back to the main loop.
- **Play Music**: Say `"Open music"`. It opens your default player with your configured `MUSIC_PATH`. While playing, you can say `"pause"`, `"play"`, `"next"`, or `"previous"` to control playback, and `"stop"` to exit back to the main assistant loop.
- **Exit Assistant**: Say `"Quit"` or `"Exit"`.
