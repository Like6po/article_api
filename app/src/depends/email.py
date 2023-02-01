from core.settings import SETTINGS
from services.email import EmailService

email_service = EmailService(host=SETTINGS.SMTP.HOST,
                             port=SETTINGS.SMTP.PORT,
                             email=SETTINGS.SMTP.EMAIL,
                             password=SETTINGS.SMTP.PASSWORD)


def get_email_service() -> EmailService:
    return email_service
