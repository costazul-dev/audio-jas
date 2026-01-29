# Audio JAS

Email-based audio transcription service. Send an audio file, receive a transcript.

## Features

- Email an audio file → receive transcript as reply
- Supports .mp3, .wav, .m4a, .ogg
- Whitelist-based access control

## Tech Stack

- Python
- OpenAI Whisper API
- IMAP (PurelyMail)
- ffmpeg (audio conversion)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your configuration:
   ```
   cp .env.example .env
   ```
5. Install ffmpeg (system dependency, required for audio conversion):
   ```
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg
   ```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI API key for Whisper | (required) |
| `IMAP_HOST` | IMAP server hostname | (required) |
| `IMAP_PORT` | IMAP server port | `993` |
| `IMAP_USERNAME` | IMAP login username | (required) |
| `IMAP_PASSWORD` | IMAP login password | (required) |
| `POLL_INTERVAL` | Seconds between inbox checks | `5` |
| `FFMPEG_PATH` | Path to ffmpeg binary | system default |
| `OUTPUT_DIR` | Directory for transcription output | (required) |

## Architecture

- `src/transcription.py` - audio-to-text via OpenAI Whisper API with ffmpeg normalization
- `src/email_client.py` - IMAP connection, inbox polling, audio attachment extraction

Processed emails are moved from INBOX to a `Processed` folder.

## Usage

[Work in progress]
