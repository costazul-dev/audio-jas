import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, parseaddr
from pathlib import Path

from .email_client import EmailMessage

logger = logging.getLogger(__name__)


class EmailSenderError(Exception):
    pass


class SMTPConnectionError(EmailSenderError):
    pass


class SMTPAuthenticationError(EmailSenderError):
    pass


class SendError(EmailSenderError):
    pass


class EmailSender:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self._host = host or os.environ.get("SMTP_HOST", "")
        self._port = port or int(os.environ.get("SMTP_PORT", "465"))
        self._username = username or os.environ.get("SMTP_USERNAME", "")
        self._password = password or os.environ.get("SMTP_PASSWORD", "")
        self._connection: smtplib.SMTP | smtplib.SMTP_SSL | None = None

    def connect(self) -> None:
        try:
            if self._port == 465:
                self._connection = smtplib.SMTP_SSL(self._host, self._port)
            else:
                self._connection = smtplib.SMTP(self._host, self._port)
                self._connection.starttls()
        except Exception as e:
            raise SMTPConnectionError(
                f"Failed to connect to {self._host}:{self._port}: {e}"
            )

        try:
            self._connection.login(self._username, self._password)
        except Exception as e:
            self._connection = None
            raise SMTPAuthenticationError(
                f"SMTP login failed for {self._username}: {e}"
            )

        logger.info("Connected to SMTP server %s:%d", self._host, self._port)

    def disconnect(self) -> None:
        if self._connection:
            try:
                self._connection.quit()
            except Exception:
                pass
            self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False

    def send_transcript(
        self, original: EmailMessage, transcript_paths: list[Path]
    ) -> None:
        if not self._connection:
            raise SMTPConnectionError("Not connected. Call connect() first.")

        _, recipient = parseaddr(original.sender)
        if not recipient:
            raise SendError(f"Cannot parse recipient from: {original.sender}")

        msg = MIMEMultipart()
        msg["From"] = formataddr(("", self._username))
        msg["To"] = recipient
        msg["Date"] = formatdate(localtime=True)

        subject = original.subject or ""
        msg["Subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject

        if original.message_id:
            msg["In-Reply-To"] = original.message_id
            msg["References"] = original.message_id

        body = "Your audio file has been transcribed. The transcript is attached."
        msg.attach(MIMEText(body, "plain"))

        for path in transcript_paths:
            with open(path, "rb") as f:
                attachment = MIMEApplication(f.read(), Name=path.name)
            attachment["Content-Disposition"] = f'attachment; filename="{path.name}"'
            msg.attach(attachment)

        try:
            self._connection.sendmail(self._username, recipient, msg.as_string())
        except Exception as e:
            raise SendError(f"Failed to send reply to {recipient}: {e}")

        logger.info("Sent transcript reply to %s", recipient)
