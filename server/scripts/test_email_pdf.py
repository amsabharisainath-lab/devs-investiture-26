"""Smoke-test registration email, OD PDF creation, and OD email delivery.

Run from the server container:
    python scripts/test_email_pdf.py

Required environment variables:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
    EMAIL_TEST_TO
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

from pypdf import PdfReader

# Test-only path bootstrap: this script is launched as /app/scripts/*.py,
# so Python does not automatically add the project root containing app/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.dependancies.create_od_pdf import create_student_od_task
from app.dependancies.email_format import send_registration_email
from app.dependancies.send_email import send_email
from app.worker.tasks import get_investiture_od_email_html


REQUIRED_ENVIRONMENT = (
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "EMAIL_TEST_TO",
)


def required_environment() -> dict[str, str]:
    missing = [name for name in REQUIRED_ENVIRONMENT if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    return {name: os.environ[name] for name in REQUIRED_ENVIRONMENT}


def test_pdf_creation() -> bytes:
    # Keep these values identical to create_od_pdf.py's existing local test.
    department_name = "Computer Science and Engineering"
    student_name = "Kamlesh"
    roll_number = "250701314"
    year = "3"

    pdf_bytes = create_student_od_task(
        department_name=department_name,
        student_name=student_name,
        roll_number=roll_number,
        year=year,
    )

    if not pdf_bytes.startswith(b"%PDF"):
        raise AssertionError("PDF output does not start with a PDF signature")

    reader = PdfReader(__import__("io").BytesIO(pdf_bytes))
    if len(reader.pages) == 0:
        raise AssertionError("Generated PDF has no pages")

    output_path = Path(os.getenv("PDF_TEST_OUTPUT", "/tmp/devs_od_request_final.pdf"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)

    digest = hashlib.sha256(pdf_bytes).hexdigest()
    print(f"PASS PDF creation: {len(pdf_bytes)} bytes, {len(reader.pages)} page(s)")
    print(f"     SHA-256: {digest}")
    print(f"     Saved: {output_path}")
    return pdf_bytes


def test_registration_email(receiver_email: str) -> None:
    sent = send_registration_email(
        receiver_email=receiver_email,
        name="Email PDF Test Student",
        registration_id="PDF-TEST-001",
        department_year="Computer Science and Engineering, 3rd Year",
        event_time="09:00 AM",
        event_venue="Main Auditorium",
        website_link="https://devsrec.com",
    )
    if not sent:
        raise RuntimeError("Registration email sender returned False")
    print(f"PASS registration email: sent to {receiver_email}")


def test_od_email(receiver_email: str, pdf_bytes: bytes) -> None:
    sent = send_email(
        receiver_email=receiver_email,
        subject="TEST - OD Letter: Investiture Ceremony",
        html_content=get_investiture_od_email_html("Kamlesh"),
        pdf_bytes=pdf_bytes,
        pdf_filename="OD_CS2026101.pdf",
    )
    if not sent:
        raise RuntimeError("OD email sender returned False")
    print(f"PASS OD email with PDF attachment: sent to {receiver_email}")


def main() -> None:
    environment = required_environment()
    receiver_email = environment["EMAIL_TEST_TO"]
    pdf_bytes = test_pdf_creation()
    test_registration_email(receiver_email)
    test_od_email(receiver_email, pdf_bytes)
    print("ALL EMAIL/PDF TESTS PASSED")


if __name__ == "__main__":
    main()
