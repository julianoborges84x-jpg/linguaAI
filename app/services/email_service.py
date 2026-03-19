import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)

def build_verification_url(token: str) -> str:
    return f"{settings.frontend_url.rstrip('/')}/verify-email?token={token}"


def send_verification_email(email: str, token: str) -> bool:
    verify_url = build_verification_url(token)

    message = MIMEMultipart()
    message["From"] = settings.email_from or "no-reply@mentorlingua.local"
    message["To"] = email
    message["Subject"] = "Confirmar cadastro - Mentor Lingua"

    body = f"""
Olá!

Clique no link abaixo para confirmar seu cadastro:

{verify_url}

Se você não criou essa conta, ignore este e-mail.

Equipe Mentor Lingua
"""

    message.attach(MIMEText(body, "plain"))

    if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password, settings.email_from]):
        logger.warning("SMTP not configured; verification email skipped for %s", email)
        return False

    try:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10)
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(
            settings.email_from,
            email,
            message.as_string()
        )

        server.quit()
        return True
    except Exception as e:
        logger.exception("Erro ao enviar email de verificacao para %s", email)
        return False
