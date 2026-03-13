import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_verification_email(email: str, token: str):

    verify_url = f"{settings.frontend_url}/verify-email?token={token}"

    message = MIMEMultipart()
    message["From"] = settings.email_from
    message["To"] = email
    message["Subject"] = "Confirmar cadastro - Mentor Lingua"

    body = f"""
Olá!

Clique no link abaixo para confirmar seu cadastro:

{verify_url}

Se você não criou essa conta, ignore este e-mail.
"""

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
    server.starttls()

    server.login(settings.smtp_user, settings.smtp_password)

    server.sendmail(
        settings.email_from,
        email,
        message.as_string()
    )

    server.quit()