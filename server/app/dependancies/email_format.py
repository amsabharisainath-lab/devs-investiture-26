import time
from app.dependancies.send_email import send_email
from pathlib import Path

def send_registration_email(
    receiver_email: str,
    name: str,
    registration_id: str,
    department_year: str,
    event_time: str,
    event_venue: str,
    website_link: str,
    event_name: str = "Investiture Ceremony of DEVS REC"
) -> bool:
    """
    Prepares the template, assets, and subject for the Investiture Ceremony email,
    then dispatches it via the generic send_email function.
    """
    subject: str = f"Your Spot is Confirmed | {event_name}"
    
    # Generate a unique timestamp to prevent email clients from trimming the content (the three dots)
    unique_id = time.time()

    # Using an f-string to inject the dynamic variables passed from the calling function
    html_content: str = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
        <img src="cid:header_image" alt="DEVS Banner" style="max-width: 100%; height: auto; margin-bottom: 20px;">

        <p>Dear <strong>{name}</strong>,</p>

        <p>Your registration for <strong>{event_name}</strong> is confirmed!</p>

        <p>We are happy to invite you to the Investiture Ceremony of DEVS REC. Your presence makes this occasion even more special as we turn the page to a new chapter. Come witness the induction of the new team and be part of this memorable moment.</p>

        <p>Your registration has been recorded under <strong>{registration_id}</strong>, as a <strong>{department_year}</strong> student. The event will be held on 8th October, from <strong>{event_time}</strong>, at <strong>{event_venue}</strong>. Kindly make sure you arrive at the venue on time.</p>

        <p>Please note that your entry/exit QR code can be accessed through the website <a href="{website_link}">{website_link}</a> and will be scanned at the venue.</p>

        <p>See you there!</p>

        <p>Warm Regards,<br>
        <strong>DEVS REC</strong></p>
        
        <!-- Hidden unique identifier to prevent email clients from clipping content -->
        <div style="display: none; opacity: 0; max-height: 0px; font-size: 0px; line-height: 0px; overflow: hidden; mso-hide: all;">
            {unique_id}
        </div>
    </body>
    </html>
    """

    # Map the Content-ID "header_image" to the local file
    images: dict[str, Path] = {
        "header_image": Path(__file__).resolve().parent / "DEVS_registration.png"
    }

    # Call the generic service
    return send_email(
        receiver_email=receiver_email,
        subject=subject,
        html_content=html_content,
        inline_images=images
    )