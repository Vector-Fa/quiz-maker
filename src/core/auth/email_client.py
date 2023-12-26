import smtplib
import ssl
from email.message import EmailMessage

from src.core.config import settings


class EmailClient:
    context = ssl.create_default_context()

    def __init__(self, sender: EmailMessage):
        self.msg = sender

    def send(self, to_email: str, verify_code: int):
        self._set_configs(to_email, verify_code)
        self._send_email()

    def _set_configs(self, to_email: str, verify_code: int):
        self.msg["Subject"] = "verify code"
        self.msg["From"] = settings.EMAIL_HOST_USER
        self.msg["To"] = to_email
        self.msg.set_content(f"verify code: {verify_code}")

    def _send_email(self):
        with smtplib.SMTP_SSL(
            settings.EMAIL_HOST, settings.EMAIL_HOST_PORT, context=self.context
        ) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(self.msg)


def get_email_sender() -> EmailClient:
    return EmailClient(EmailMessage())
