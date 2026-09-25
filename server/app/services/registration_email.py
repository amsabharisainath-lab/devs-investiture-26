from sqlalchemy.orm import Session

from app.dependancies.email_format import send_registration_email
from app.models.registration import Registration


def send_registration_email_now(
    registration: Registration,
    db: Session,
) -> None:
    """Send the existing formatted registration email for a persisted record."""
    user = registration.user
    
    if not user or not user.email:
        raise ValueError(
            f"Registration {registration.id} has no recipient email address"
        )

    # 1. Get the Registration ID
    # Since your Registration model uses `id` as the primary key
    # Use the student's roll number as the registration ID, with a fallback if it's empty
    reg_id = user.roll_no if user.roll_no else "N/A"
    
    # 2. Extract Department and Year from the User model
    # Handling nullable fields just in case they aren't filled
    department = user.department if user.department else "N/A"
    
    if user.year == 1:
        year_str = "1st Year"
    elif user.year == 2:
        year_str = "2nd Year"
    elif user.year == 3:
        year_str = "3rd Year"
    elif user.year:
        year_str = f"{user.year}th Year"
    else:
        year_str = "Unknown Year"

    department_year = f"{department}, {year_str}"

    # 3. Define the event specifics 
    # (Adjust these variables as necessary for your actual event)
    event_time = "10:00 AM"               
    event_venue = "Main Auditorium"       
    website_link = "https://devsrec.com"  
    
    # 4. Call the updated email function
    is_sent = send_registration_email(
        receiver_email=user.email,
        name=user.name,
        registration_id=reg_id,
        department_year=department_year,
        event_time=event_time,
        event_venue=event_venue,
        website_link=website_link
    )

    if not is_sent:
        raise RuntimeError(
            f"Registration email delivery failed for {user.email}"
        )