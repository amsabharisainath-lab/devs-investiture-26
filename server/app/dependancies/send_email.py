import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from pathlib import Path

def send_email(
    receiver_email: str,
    subject: str,
    html_content: str,
    inline_images: dict[str, str | Path] | None = None,
) -> bool:
    """
    Generic utility to send emails with optional inline images or attachments.
    """
    # Note: In a production app, load these from environment variables (e.g., python-dotenv)
    sender_email: str = "kamlesh.a2007@gmail.com"
    password: str = "kqlq uukn ppqg kbmo"

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
                print(f"Error: Image file not found at {path}")
                return False
            
            with path.open("rb") as img_file:
                img = MIMEImage(img_file.read(), name=path.name)
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=path.name)
                message.attach(img)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False