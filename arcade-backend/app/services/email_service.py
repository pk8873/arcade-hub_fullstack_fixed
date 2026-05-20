"""Email service - SMTP with console fallback for local dev.

Works with any free SMTP provider:
  - Gmail (use an App Password, not your normal password)
  - Brevo (Sendinblue) - free 300/day
  - Mailtrap - free dev sandbox
  - Mailgun sandbox
Configure via SMTP_* env vars.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from app.config import settings

logger = logging.getLogger("email")


def _build_message(to: str, subject: str, html: str, text: Optional[str] = None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text or "This email requires an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    return msg


def send_email(to: str, subject: str, html: str, text: Optional[str] = None) -> bool:
    """Send an email. Falls back to console logging if SMTP isn't configured."""
    msg = _build_message(to, subject, html, text)

    if not settings.smtp_host or not settings.smtp_user:
        if settings.email_console_fallback:
            logger.warning("[EMAIL:CONSOLE] To=%s Subject=%s\n%s", to, subject, html)
            return True
        logger.error("SMTP not configured and console fallback disabled.")
        return False

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20) as s:
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as s:
                s.ehlo()
                if settings.smtp_tls:
                    s.starttls()
                    s.ehlo()
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        logger.info("Email sent to %s subject=%s", to, subject)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("Email send failed: %s", exc)
        if settings.email_console_fallback:
            logger.warning("[EMAIL:CONSOLE-FALLBACK] To=%s Subject=%s\n%s", to, subject, html)
            return True
        return False


def send_verification_email(to: str, username: str, token: str) -> bool:
    verify_url = f"{settings.backend_url}/api/auth/verify?token={token}"
    frontend_url = f"{settings.frontend_url}/verify?token={token}"
    html = f"""
<!doctype html>
<html><body style="font-family:Arial,sans-serif;background:#0b1020;color:#e6e8ef;padding:24px">
  <div style="max-width:520px;margin:0 auto;background:#141a36;border-radius:14px;padding:28px">
    <h1 style="margin:0 0 12px;color:#a78bfa">Welcome to {settings.app_name}, {username}!</h1>
    <p style="line-height:1.5">Tap the button below to verify your email. The link works instantly &mdash; no waiting.</p>
    <p style="text-align:center;margin:28px 0">
      <a href="{frontend_url}"
         style="background:#7c3aed;color:#fff;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:600;display:inline-block">
        Verify my email
      </a>
    </p>
    <p style="font-size:12px;color:#9aa3c7">If the button doesn't work, paste this link in your browser:<br>
      <a style="color:#a78bfa" href="{frontend_url}">{frontend_url}</a><br><br>
      Or hit the backend directly: <a style="color:#a78bfa" href="{verify_url}">{verify_url}</a>
    </p>
  </div>
</body></html>"""
    return send_email(to, f"Verify your {settings.app_name} email", html)
