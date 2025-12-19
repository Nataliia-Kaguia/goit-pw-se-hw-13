import smtplib
from email.message import EmailMessage
from .config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, APP_HOST

def send_email(to: str, subject: str, body: str):
    # simple SMTP sender; in dev you can print instead if SMTP not configured
    if not SMTP_HOST:
        print(f"[EMAIL to={to}] subject={subject}\n{body}")
        return
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASSWORD)
        s.send_message(msg)

def send_verification_email(to: str, code: str):
    url = f"{APP_HOST}/auth/verify?code={code}&email={to}"
    send_email(to, "Verify your account", f"Click to verify: {url}")

def send_reset_email(to: str, code: str):
    url = f"{APP_HOST}/auth/reset-password?code={code}&email={to}"
    send_email(to, "Reset password", f"Use this code to reset password: {code}\nOr click: {url}")
