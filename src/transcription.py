import os
import tempfile
from pathlib import Path

import ffmpeg
from openai import OpenAI, APIError, RateLimitError

SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".ogg"}
WHISPER_MAX_SIZE_MB = 25
NORMALIZED_FORMAT = "mp3"


class TranscriptionError(Exception):
    pass


class FileTooLargeError(TranscriptionError):
    pass


class InvalidFormatError(TranscriptionError):
    pass


class RateLimitExceededError(TranscriptionError):
    pass


def _get_ffmpeg_path() -> str | None:
    return os.environ.get("FFMPEG_PATH") or None


def _validate_audio_file(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise InvalidFormatError(
            f"Unsupported format: {suffix}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )

    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > WHISPER_MAX_SIZE_MB:
        raise FileTooLargeError(
            f"File size {size_mb:.1f}MB exceeds {WHISPER_MAX_SIZE_MB}MB limit"
        )


def _convert_to_normalized_format(
    input_path: Path, output_path: Path, ffmpeg_path: str | None = None
) -> None:
    try:
        stream = ffmpeg.input(str(input_path))
        stream = ffmpeg.output(
            stream,
            str(output_path),
            acodec="libmp3lame",
            ar=16000,
            ac=1,
        )
        kwargs = {"overwrite_output": True, "capture_stderr": True}
        if ffmpeg_path:
            kwargs["cmd"] = ffmpeg_path
        ffmpeg.run(stream, **kwargs)
    except ffmpeg.Error as e:
        stderr = e.stderr.decode() if e.stderr else "Unknown error"
        raise TranscriptionError(f"FFmpeg conversion failed: {stderr}")


def transcribe(
    audio_path: str | Path,
    api_key: str | None = None,
    language: str | None = None,
) -> str:
    """
    Transcribe an audio file to text using OpenAI Whisper API.

    Args:
        audio_path: Path to the audio file (.mp3, .wav, .m4a, .ogg)
        api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
        language: Optional ISO-639-1 language code (e.g., 'en', 'es').

    Returns:
        Transcribed text.

    Raises:
        FileNotFoundError: Audio file does not exist.
        InvalidFormatError: Unsupported audio format.
        FileTooLargeError: File exceeds 25MB limit.
        RateLimitExceededError: API rate limit hit.
        TranscriptionError: Other transcription failures.
    """
    audio_path = Path(audio_path)
    _validate_audio_file(audio_path)

    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise TranscriptionError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)
    ffmpeg_path = _get_ffmpeg_path()

    with tempfile.TemporaryDirectory() as tmpdir:
        normalized_path = Path(tmpdir) / f"audio.{NORMALIZED_FORMAT}"
        _convert_to_normalized_format(audio_path, normalized_path, ffmpeg_path)

        normalized_size_mb = normalized_path.stat().st_size / (1024 * 1024)
        if normalized_size_mb > WHISPER_MAX_SIZE_MB:
            raise FileTooLargeError(
                f"Converted file size {normalized_size_mb:.1f}MB exceeds {WHISPER_MAX_SIZE_MB}MB limit"
            )

        try:
            with open(normalized_path, "rb") as audio_file:
                kwargs = {"model": "whisper-1", "file": audio_file}
                if language:
                    kwargs["language"] = language
                response = client.audio.transcriptions.create(**kwargs)
            return response.text
        except RateLimitError as e:
            raise RateLimitExceededError(f"Rate limit exceeded: {e}")
        except APIError as e:
            raise TranscriptionError(f"OpenAI API error: {e}")
