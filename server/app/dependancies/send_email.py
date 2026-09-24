import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path

from app.core.config import settings


def send_email(
    receiver_email: str,
    subject: str,
    html_content: str,
    inline_images: dict[str, str | Path] | None = None,
) -> bool:
    """
    Generic utility to send emails with optional inline images or attachments.
    """
    sender_email = settings.SMTP_FROM or settings.SMTP_USER
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not sender_email:
        raise RuntimeError("SMTP_USER, SMTP_PASSWORD, and SMTP_FROM are required")

    message = MIMEMultipart("related")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the HTML body
    message.attach(MIMEText(html_content, "html"))

    # Process and attach any inline images mapped by Content-ID (CID)
    if inline_images:
        for cid, file_path in inline_images.items():
            path = Path(file_path)
            if not path.is_file():
                raise FileNotFoundError(f"Inline image not found: {path}")

            with path.open("rb") as img_file:
                img = MIMEImage(img_file.read(), name=path.name)
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=path.name)
                message.attach(img)

    try:
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        with server:
            if settings.SMTP_PORT != 465:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except smtplib.SMTPException:
        raise
