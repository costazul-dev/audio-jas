# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-07

### Added

- `src/email_sender.py` - SMTP email reply with transcript attachment
- `EmailSender` class with context manager support for SMTP connections
- `send_transcript()` sends reply to original sender with `.txt` attachments
- `In-Reply-To` and `References` headers for email threading
- SMTP_SSL (port 465) and STARTTLS support
- Custom error hierarchy: `EmailSenderError`, `SMTPConnectionError`, `SMTPAuthenticationError`, `SendError`
- `message_id` field on `EmailMessage` dataclass for reply threading
- `Message-ID` header extraction in `_parse_email()`
- SMTP configuration in `.env.example` (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`)

## [0.3.0] - 2026-01-29

### Added

- Sender whitelist via `SENDER_WHITELIST` env var (comma-separated, case-insensitive)
- Non-whitelisted emails moved to `Rejected` IMAP folder
- Per-sender subfolders under `Processed` (e.g., `Processed/user@example_com`)
- IMAP namespace delimiter detection for folder naming

### Changed

- `mark_as_processed()` now accepts `EmailMessage` instead of `uid: int`
- `_ensure_processed_folder()` replaced by `_ensure_folders()` and `_ensure_folder()`
- Whitelist check runs before `_parse_email`, preventing disk writes for rejected senders
- Empty/unset `SENDER_WHITELIST` rejects all emails (strict default)

## [0.2.0] - 2026-01-29

### Added

- `src/email_client.py` - IMAP email polling and audio attachment extraction
- `EmailClient` class with context manager support for IMAP connections
- `fetch_unseen_emails()` to retrieve all emails from INBOX with audio attachments
- `mark_as_processed()` to move processed emails to a `Processed` folder
- `EmailMessage` dataclass (uid, sender, subject, attachment_paths)
- Custom error hierarchy: `EmailClientError`, `IMAPConnectionError`, `AuthenticationError`, `FetchError`
- Auto-creation of `Processed` IMAP folder on connect
- `POLL_INTERVAL` environment variable (default: 5 seconds)
- Malformed emails are logged and skipped without interrupting batch processing
- Verified manually against PurelyMail IMAP server

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