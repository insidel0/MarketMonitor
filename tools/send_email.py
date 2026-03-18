"""Send the daily Finanzgericht digest email via Outlook SMTP + App Password.

Requires environment variables:
  OUTLOOK_ADDRESS     — the sender Outlook address (e.g. fg-monitor@outlook.com)
  OUTLOOK_APP_PASSWORD — App Password from Microsoft account security settings
  NOTIFICATION_EMAIL  — recipient address(es), comma-separated
"""
import logging
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from tools.scrapers.base import Publication

logger = logging.getLogger(__name__)

SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587


def format_email_body(
    new_publications: dict[str, list[Publication]],
) -> str:
    """Build plain-text email body grouped by court."""
    today = datetime.now().strftime("%d.%m.%Y")
    lines = [
        f"Neue Finanzgericht-Entscheidungen — {today}",
        "",
    ]

    total = sum(len(v) for v in new_publications.values())

    for court_name, pubs in new_publications.items():
        lines.append(f"─── {court_name} ({len(pubs)}) ───")
        for pub in pubs:
            date_str = f"{pub.date} — " if pub.date else ""
            lines.append(f"• {date_str}{pub.title}")
            lines.append(f"  {pub.url}")
        lines.append("")

    lines.append(
        f"Gesamt: {total} neue Entscheidung{'en' if total != 1 else ''} "
        f"aus {len(new_publications)} Gericht{'en' if len(new_publications) != 1 else ''}"
    )
    lines.append(
        f"Abruf: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} CET"
    )
    return "\n".join(lines)


def send_digest(new_publications: dict[str, list[Publication]]) -> None:
    """Send the digest email. Raises on failure."""
    sender = os.environ["OUTLOOK_ADDRESS"]
    password = os.environ["OUTLOOK_APP_PASSWORD"]
    recipients_raw = os.environ["NOTIFICATION_EMAIL"]
    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    today = datetime.now().strftime("%d.%m.%Y")
    total = sum(len(v) for v in new_publications.values())

    subject = f"Neue Finanzgericht-Entscheidungen — {today} ({total} neu)"
    body = format_email_body(new_publications)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())

    logger.info(
        "Email sent to %s: %d new publications in %d courts",
        recipients,
        total,
        len(new_publications),
    )
