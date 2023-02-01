import random
from email.message import EmailMessage

import aiosmtplib

from core.settings import SETTINGS


class SMTPSendError(Exception):
    pass


class EmailService:
    def __init__(self,
                 host: str,
                 port: int,
                 email: str,
                 password: str):
        self._host: str = host
        self._port: int = port
        self._email: str = email
        self._password: str = password

    @staticmethod
    def _generate_code() -> str:
        value = str(random.randint(0, 999999))
        return (6 - len(value)) * "0" + value

    async def _send_message(self, receiver_email: str, code: str) -> None:
        message = EmailMessage()
        message["From"] = self._email
        message["To"] = receiver_email
        message["Subject"] = "Code From Test FastAPI App"
        message.set_content(f"Hello! Your one-time code: {code}")
        try:
            await aiosmtplib.send(message, hostname=self._host, port=self._port,
                                  username=self._email, password=self._password)
        except Exception:
            raise SMTPSendError()

    async def send_code_to_email(self, email: str) -> str:
        if SETTINGS.DEBUG:
            return "123456"
        code = self._generate_code()
        await self._send_message(receiver_email=email, code=code)
        return code
