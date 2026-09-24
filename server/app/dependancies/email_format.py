from app.dependancies.send_email import send_email

def send_registration_email(receiver_email: str) -> bool:
    """
    Prepares the template, assets, and subject for the Round 2 Shortlist email,
    then dispatches it via the generic send_email function.
    """
    subject: str = "DEVS REC Board Recruitment 2026 - Round 2 Shortlist"
    
    # The template relies on cid:header_image which we map in the dictionary below
    html_content: str = """
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
        <img src="cid:header_image" alt="DEVS Banner" style="max-width: 100%; height: auto;">
        
        <p><strong>Dear Applicant,</strong></p>
        
        <p><strong>Congratulations! 🎉</strong></p>
        
        <p>We're delighted to inform you that <strong>you've been shortlisted</strong> for <strong>Round 2</strong> of the <strong>DEVS REC Board Recruitment 2026</strong>.</p>
        
        <p>Your application stood out during our initial screening, and we're excited to see you take the next step in the recruitment process. This round is an opportunity for you to showcase your skills, ideas, and unique perspective.</p>
        
        <p>To ensure smooth communication throughout the Round 2 stage of the recruitment process, we have created an official WhatsApp group for all shortlisted candidates.</p>
        
        <p><strong>Please join the group using the link below:</strong><br>
        🔗 <a href="https://chat.whatsapp.com/EslL7JlUP3kJ5K1fn8ujqk">https://chat.whatsapp.com/EslL7JlUP3kJ5K1fn8ujqk</a></p>
        
        <p><strong>All updates regarding your Round 2 schedule, date, time, panel allocation, domain-specific instructions, and other important announcements will be shared through this group.</strong></p>
    </body>
    </html>
    """

    # Map the Content-ID "header_image" to the local file
    images: dict[str, str] = {
        "header_image": "DEVS_registration.png"
    }

    # Call the generic service
    return send_email(
        receiver_email=receiver_email,
        subject=subject,
        html_content=html_content,
        inline_images=images
    )