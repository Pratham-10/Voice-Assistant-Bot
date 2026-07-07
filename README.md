# Autonomous AI Voice Agent

An event-driven, cross-platform voice assistant built as an autonomous AI agent using Gemini function-calling orchestration. The system processes natural language queries to control local environments and remote APIs, utilizing a thread-safe state machine to coordinate audio, background workers, and external integrations.

## Architecture & System Design

The system is built on a modular, agentic architecture:

* **Speech Processing**: Audio capture is handled via PyAudio and SpeechRecognition, configured with optimized silence thresholds. Text-to-speech runs via native subprocesses on macOS (utilizing the `say` command for low-latency offline synthesis) and COM-based SAPI5/espeak wrappers on Windows/Linux.
* **Autonomous Agent Orchestrator**: Powered by `gemini-2.5-flash` using function-calling. Natural language queries are mapped dynamically to registered Python tools, avoiding legacy regex/substring routing.
* **Asynchronous Coordinator & State Machine**: A thread-safe state machine (`State`) manages the assistant's runtime state (`IDLE`, `LISTENING`, `THINKING`, `SPEAKING`).
* **State-Aware Background Reminders**: A SQLite-backed background worker monitors pending reminders. To prevent audio collisions, the background thread queries the state machine: if the assistant is not `IDLE`, reminders bypass TTS and are routed to macOS notification banners and stdout.

---

## Agentic Capabilities & Features

* **Autonomous Tool Selection & Execution (Function-Calling)**: Dynamically reasons about user intent to choose and execute the correct tools (Google Calendar, Spotify, Gmail, Web Search) from a registered functional schema, including resolving relative date/time arguments (e.g., "tomorrow at 4pm") based on current local context.
* **Cross-App Integration & Fallback Routing**: Bridges multiple APIs. For example, music playback queries initiate Spotify Web API commands and dynamically fall back to browser-based YouTube streaming via DuckDuckGo search if endpoints are unavailable or unconfigured.
* **Google OAuth 2.0 Integration**: Supports secure, desktop-initiated OAuth flows for Google Calendar (complete CRUD with automatic primary timezone synchronization) and Gmail.
* **Asynchronous Background Processing**: A SQLite-powered background daemon runs reminders in a separate thread, implementing a state-aware callback to prevent interrupting active voice synthesis or capture.
* **DuckDuckGo Web Search Integration**: Real-time web queries using `ddgs` to retrieve snippets for current events.

---

## Installation

### Prerequisites

#### System Dependencies (PortAudio)
Speech recognition requires system-level audio headers.

* **macOS**:
  ```bash
  brew install portaudio
  ```
* **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt-get update && sudo apt-get install portaudio19-dev python3-pyaudio espeak
  ```
* **Windows**:
  No additional system dependencies are required.

### Setup

1. **Clone and Initialize Environment**:
   ```bash
   git clone
   cd Voice-Assistant-Bot
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory (see `.env.example`):
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   WEATHER_API_KEY=your_openweathermap_api_key
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   GOOGLE_CREDENTIALS_PATH=your-credential-json path
   ```

3. **Google API Setup**:
   * Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   * Enable the **Google Calendar API** and **Gmail API**.
   * Configure the OAuth Consent Screen (Internal/External) and add your email to **Test Users**.
   * Under **Credentials**, create an **OAuth Client ID** for a **Desktop Application**.
   * Download the JSON credentials file, rename it to `credentials.json`, and place it in the root directory.
   * On first run, follow the browser-based OAuth flow to authorize access. The credentials will be cached in `token.json`.

---

## Running the Application

Start the main loop:
```bash
python3 main.py
```

### Voice Commands Examples
* **Calendar Management**: 
  - *"Schedule a meeting tomorrow at 4:00 PM for 30 minutes"*
  - *"What meetings do I have scheduled?"*
  - *"Reschedule Code Review to next Monday at 2:00 PM"*
* **Communication**: *"Send an email to user@example.com with subject Hi"*
* **Reminders**: *"Set a reminder in two minutes to drink water"*
* **System/Music Control**: *"Play Blinding Lights"* or *"Pause the music"*

---

## Testing

Run the automated test suite verifying the registered tools, Spotify fallbacks, and Calendar CRUD mock interactions:
```bash
python3 -m unittest tests/test_tools.py
```
