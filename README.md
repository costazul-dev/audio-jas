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

## Usage

[Work in progress]
