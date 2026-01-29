# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-29

### Added

- `src/transcription.py` - audio-to-text transcription using OpenAI Whisper API
- `transcribe()` function accepting audio file path with optional language and API key parameters
- FFmpeg-based audio normalization (converts to mono MP3 at 16kHz before API call)
- Support for .mp3, .wav, .m4a, .ogg input formats
- File validation (existence, format, 25MB size limit)
- Custom error hierarchy: `TranscriptionError`, `FileTooLargeError`, `InvalidFormatError`, `RateLimitExceededError`
- Verified manually with Spanish audio input

## [0.0.0] - 2026-01-28

### Added

- Initial project structure with `src/` directory
- `requirements.txt` with core dependencies (ffmpeg-python, imapclient, openai, python-dotenv)
- `.env.example` template for environment configuration
- `.gitignore` for Python projects
- `README.md` with project overview