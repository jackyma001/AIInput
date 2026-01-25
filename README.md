# AIInput

[Chinese Version (中文版)](./README_ZH.md)

A high-performance voice input tool for Windows that transcribes speech in real-time and types it wherever you are.

## Features

- **Global Hotkey**: Press `Ctrl + Space` (default) or `Right Ctrl` (configurable alternative) to start/stop recording.
- **Audio Recording**: Captures microphone input.
- **AI Transcription**: Uses OpenAI's Whisper model locally to transcribe speech to text.
- **Text Injection**: Types the transcribed text into the active window.
- **Tray Icon**: Manage the application from the system tray.

## Installation

1. Install Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: You may need to install ffmpeg for Whisper.*

## Usage

1. Run the application:
   ```bash
   python src/main.py
   ```
2. Press the hotkey to start recording.
3. Speak.
4. Release the hotkey (or press again depending on mode) to stop and transcribe.
5. The text will be typed into your active cursor position.
