import dataclasses
import email
import logging
import os
from email.message import Message
from pathlib import Path

from imapclient import IMAPClient

SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".ogg"}
DEFAULT_POLL_INTERVAL = 5
PROCESSED_FOLDER = "Processed"

logger = logging.getLogger(__name__)


class EmailClientError(Exception):
    pass


class IMAPConnectionError(EmailClientError):
    pass


class AuthenticationError(EmailClientError):
    pass


class FetchError(EmailClientError):
    pass


@dataclasses.dataclass
class EmailMessage:
    uid: int
    sender: str
    subject: str
    attachment_paths: list[Path]


def _get_poll_interval() -> int:
    try:
        return int(os.environ.get("POLL_INTERVAL", DEFAULT_POLL_INTERVAL))
    except ValueError:
        return DEFAULT_POLL_INTERVAL


def _extract_audio_attachment(part: Message, download_dir: Path) -> Path | None:
    filename = part.get_filename()
    if not filename:
        return None

    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_AUDIO_FORMATS:
        return None

    filepath = download_dir / filename
    payload = part.get_payload(decode=True)
    if not payload:
        return None

    filepath.write_bytes(payload)
    return filepath


def _parse_email(
    uid: int, raw_bytes: bytes, download_dir: Path
) -> EmailMessage | None:
    try:
        msg = email.message_from_bytes(raw_bytes)
    except Exception:
        logger.warning("Failed to parse email UID %d", uid)
        return None

    sender = msg.get("From", "")
    subject = msg.get("Subject", "")
    attachment_paths: list[Path] = []

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        path = _extract_audio_attachment(part, download_dir)
        if path:
            attachment_paths.append(path)

    if not attachment_paths:
        return None

    return EmailMessage(
        uid=uid,
        sender=sender,
        subject=subject,
        attachment_paths=attachment_paths,
    )


class EmailClient:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self._host = host or os.environ.get("IMAP_HOST", "")
        self._port = port or int(os.environ.get("IMAP_PORT", "993"))
        self._username = username or os.environ.get("IMAP_USERNAME", "")
        self._password = password or os.environ.get("IMAP_PASSWORD", "")
        self._client: IMAPClient | None = None

    def connect(self) -> None:
        try:
            self._client = IMAPClient(self._host, port=self._port, ssl=True)
        except Exception as e:
            raise IMAPConnectionError(f"Failed to connect to {self._host}:{self._port}: {e}")

        try:
            self._client.login(self._username, self._password)
        except Exception as e:
            self._client = None
            raise AuthenticationError(f"Login failed for {self._username}: {e}")

        self._client.select_folder("INBOX")
        self._ensure_processed_folder()

    def disconnect(self) -> None:
        if self._client:
            try:
                self._client.logout()
            except Exception:
                pass
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    def _ensure_processed_folder(self) -> None:
        if not self._client:
            return
        if not self._client.folder_exists(PROCESSED_FOLDER):
            self._client.create_folder(PROCESSED_FOLDER)
            logger.info("Created folder: %s", PROCESSED_FOLDER)

    def fetch_unseen_emails(self, download_dir: Path) -> list[EmailMessage]:
        if not self._client:
            raise IMAPConnectionError("Not connected. Call connect() first.")

        try:
            uids = self._client.search("ALL")
        except Exception as e:
            raise FetchError(f"IMAP search failed: {e}")

        if not uids:
            return []

        try:
            raw_messages = self._client.fetch(uids, ["RFC822"])
        except Exception as e:
            raise FetchError(f"IMAP fetch failed: {e}")

        results: list[EmailMessage] = []
        for uid, data in raw_messages.items():
            raw_bytes = data.get(b"RFC822")
            if not raw_bytes:
                logger.warning("No RFC822 data for UID %d, skipping", uid)
                continue

            parsed = _parse_email(uid, raw_bytes, download_dir)
            if parsed:
                results.append(parsed)

        return results

    def mark_as_processed(self, uid: int) -> None:
        if not self._client:
            raise IMAPConnectionError("Not connected. Call connect() first.")

        try:
            self._client.move([uid], PROCESSED_FOLDER)
        except Exception as e:
            raise FetchError(f"Failed to move UID {uid} to {PROCESSED_FOLDER}: {e}")
