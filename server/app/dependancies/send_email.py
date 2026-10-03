import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication  # Added for PDF
from pathlib import Path

from app.core.config import settings


def send_email(
    receiver_email: str,
    subject: str,
    html_content: str,
    inline_images: dict[str, str | Path] | None = None,
    pdf_bytes: bytes | None = None,             # NEW: Optional PDF bytes
    pdf_filename: str = "OD_Document.pdf",      # NEW: Optional PDF filename
) -> bool:
    """
    Generic utility to send emails with optional inline images or attachments.
    """
    sender_email = settings.SMTP_FROM or settings.SMTP_USER
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not sender_email:
        raise RuntimeError("SMTP_USER, SMTP_PASSWORD, and SMTP_FROM are required")

    # Step 1: Build the core HTML and Inline Images EXACTLY as before
    body_message = MIMEMultipart("related")
    body_message.attach(MIMEText(html_content, "html"))

    if inline_images:
        for cid, file_path in inline_images.items():
            path = Path(file_path)
            if not path.is_file():
                raise FileNotFoundError(f"Inline image not found: {path}")

            with path.open("rb") as img_file:
                img = MIMEImage(img_file.read(), name=path.name)
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=path.name)
                body_message.attach(img)

    # Step 2: Determine final message structure based on attachments
    if pdf_bytes:
        # If we have an attachment, standard email protocol requires a "mixed" root container
        message = MIMEMultipart("mixed")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        
        # Attach the HTML/Images body
        message.attach(body_message)
        
        # Attach the PDF
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header("Content-Disposition", "attachment", filename=pdf_filename)
        message.attach(pdf_attachment)
    else:
        # ORIGINAL BEHAVIOR: If no PDF, the 'related' container is the root message
        message = body_message
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

    # Step 3: Send the email
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