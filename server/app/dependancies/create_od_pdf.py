from __future__ import annotations

import base64
import html
import io
import os
from pathlib import Path

import pdfkit
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import shutil

wkhtmltopdf_path = shutil.which("wkhtmltopdf")


# ============================================================
# Helper: convert image to Base64
# ============================================================

def image_to_data_uri(image_path: Path) -> str:
    """
    Convert an image into a Base64 data URI.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found:\n{image_path}")

    extension = image_path.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }

    mime_type = mime_types.get(extension)
    if mime_type is None:
        raise ValueError(f"Unsupported image format: {extension}")

    try:
        image_bytes = image_path.read_bytes()
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        raise RuntimeError(f"Failed to process image {image_path}: {str(e)}")


# ============================================================
# Helper: safely insert dynamic values into HTML
# ============================================================

def safe_text(value: str) -> str:
    return html.escape(str(value))


# ============================================================
# Generate Raw OD PDF (In-Memory)
# ============================================================

def generate_od_pdf(
    department_name: str,
    student_name: str,
    roll_number: str,
    year: str,
) -> bytes:
    """
    Generates a professional single-page A4 OD letter.
    Returns the raw PDF bytes.
    """
    try:
        base_dir = Path(__file__).resolve().parent

        header_path = base_dir / "OD Letter Header.png"
        coordinator_sign_path = base_dir / "OD Letter Header.png"
        president_sign_path = base_dir / "OD Letter Header.png"

        required_files = {
            "Header image": header_path,
            "Coordinator signature": coordinator_sign_path,
            "President signature": president_sign_path,
        }

        for description, file_path in required_files.items():
            if not file_path.exists():
                raise FileNotFoundError(f"{description} not found at expected path: {file_path}")

        header_img = image_to_data_uri(header_path)
        coordinator_img = image_to_data_uri(coordinator_sign_path)
        president_img = image_to_data_uri(president_sign_path)

        department_name = safe_text(department_name)
        student_name = safe_text(student_name)
        roll_number = safe_text(roll_number)
        year = safe_text(year)

        event_name = safe_text("DEVS REC Investiture Ceremony")
        event_date = safe_text("15 October 2026")
        event_start = safe_text("09:00 AM")
        event_end = safe_text("01:00 PM")
        event_venue = safe_text("Main Auditorium")

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>DEVS REC On-Duty Request</title>
<style>
/* ==========================================================
   A4 PAGE CONSTRAINTS (CSS Table Layout)
   ========================================================== */
html, body {{
    margin: 0;
    padding: 0;
    height: 100%; 
    font-family: "Times New Roman", serif;
    font-size: 11pt;
    line-height: 1.45; 
    color: #000;
    background-color: transparent;
}}

.page {{
    display: table;
    width: 100%;
    height: 100%; 
}}

.content-row {{
    display: table-row;
    height: 100%; 
}}

.content-cell {{
    display: table-cell;
    vertical-align: top;
}}

.bottom-row {{
    display: table-row;
    height: 1px; 
}}

.bottom-cell {{
    display: table-cell;
    vertical-align: bottom;
}}

/* ==========================================================
   HEADER & TYPOGRAPHY
   ========================================================== */
.header {{
    width: 100%;
    border-bottom: 2px solid #000;
    padding-bottom: 3mm;
    margin-bottom: 5mm; 
}}

.header-image {{
    width: 100%;
    height: 38mm; 
    object-fit: contain;
}}

.address-section {{
    margin-bottom: 5mm;
}}

.address-heading {{
    font-weight: bold;
}}

.address-content {{
    padding-left: 12mm; 
    margin-top: 1mm;    
}}

.subject {{
    text-align: left; 
    font-weight: bold;
    font-size: 14pt;
    margin: 4mm 0 6mm; 
}}

.salutation {{
    font-weight: bold;
    margin-bottom: 2mm;
}}

.paragraph {{
    text-align: justify;
    margin-bottom: 4mm;
}}

.indented-para {{
    text-indent: 25mm; 
}}

/* ==========================================================
   EVENT TABLE 
   ========================================================== */
.event-table {{
    width: 80%; 
    margin-left: auto; 
    margin-right: auto;
    border-collapse: collapse;
    margin-top: 3mm;
    margin-bottom: 3mm;
}}

.event-table td {{
    border: 1px solid #000;
    padding: 1mm;
    font-size: 13pt; 
}}

.event-label {{
    width: 45mm;
    font-weight: bold;
}}

.closing {{
    margin-top: 5mm;
}}

.closing p {{
    margin: 0 0 5mm;
}}

.president-name {{
    font-weight: bold;
}}

/* ==========================================================
   SIGNATURE & FOOTER 
   ========================================================== */
.signature-section {{
    width: 100%;
    margin-bottom: 2mm; 
}}

.signature-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}}

.signature-table td {{
    width: 50%;
    text-align: center;
    vertical-align: bottom;
}}

.signature-image {{
    width: 40mm;
    height: 12mm;
    object-fit: contain;
    margin-bottom: 2mm;
}}

.signature-title {{
    font-weight: bold;
    font-size: 11pt;
}}

.signature-name {{
    font-size: 10.5pt;
}}

.footer {{
    width: 100%;
    border-top: 1px solid #888;
    padding-top: 2mm;
    text-align: center;
    font-size: 10pt;
    color: #555;
}}
</style>
</head>
<body>
<div class="page">
    <div class="content-row">
        <div class="content-cell">
            <div class="header">
                <img src="{header_img}" class="header-image" alt="DEVS REC Header">
            </div>
            
            <div class="address-section">
                <div class="address-heading">FROM:</div>
                <div class="address-content">The President, DEVS REC</div>
                
                <div class="address-heading" style="margin-top: 4mm;">TO:</div>
                <div class="address-content">
                    The Head of the Department,<br>
                    {department_name}
                </div>
            </div>
            
            <div class="subject">
                Subject: Request for On-Duty Permission for {event_name}
            </div>
            
            <div class="salutation">
                Respected Sir/Madam,
            </div>
            
            <p class="paragraph indented-para">
                This is to kindly request <strong>On-Duty permission</strong> for <strong>{student_name}</strong>, bearing Roll Number <strong>{roll_number}</strong>, a student of <strong>{department_name} - Year {year}</strong>, to attend and participate in the <strong>{event_name}</strong> organized by the DEVS Club as part of the formal induction and commencement of the new leadership term.
            </p>
            
            <p class="paragraph">
                The event is scheduled to be conducted on the following date, time, and venue:
            </p>
            
            <table class="event-table">
                <tr>
                    <td class="event-label">Event</td>
                    <td>{event_name}</td>
                </tr>
                <tr>
                    <td class="event-label">Date</td>
                    <td>{event_date}</td>
                </tr>
                <tr>
                    <td class="event-label">Time</td>
                    <td>{event_start} to {event_end}</td>
                </tr>
                <tr>
                    <td class="event-label">Venue</td>
                    <td>{event_venue}</td>
                </tr>
            </table>
            
            <p class="paragraph">
                The participation of the student is required to support the formal induction of the new office bearers and the commencement of their responsibilities for the upcoming term.
            </p>
            
            <p class="paragraph">
                We therefore kindly request you to grant the necessary <strong>On-Duty permission</strong> for the above-mentioned student for the specified date and duration.
            </p>
            
            <div class="closing">
                <p style="text-align: center; margin-bottom: 6mm;">Thank you.</p>
                <p>Yours sincerely,</p>
                <p>
                    <span class="president-name">Akash Vardhan V.</span><br>
                    President, DEVS REC
                </p>
            </div>
        </div>
    </div>
    
    <div class="bottom-row">
        <div class="bottom-cell">
            <div class="signature-section">
                <table class="signature-table">
                    <tr>
                        <td>
                            <img src="{coordinator_img}" class="signature-image" alt="Coordinator Signature">
                            <div class="signature-title">Club Coordinators</div>
                            <div class="signature-name">Dr. Revathy P &amp; Ms. Sorna Shanthi D</div>
                        </td>
                        <td>
                            <img src="{president_img}" class="signature-image" alt="President Signature">
                            <div class="signature-title">President, DEVS REC</div>
                            <div class="signature-name">Akash Vardhan V.</div>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="footer">
                DEVS REC &nbsp;|&nbsp; Official On-Duty Permission Request
            </div>
        </div>
    </div>
</div>
</body>
</html>
"""

        options = {
            "page-size": "A4",
            "orientation": "Portrait",
            "margin-top": "5mm",
            "margin-bottom": "0mm",
            "margin-left": "10mm",
            "margin-right": "10mm",
            "encoding": "UTF-8",
            "dpi": "300",                   
            "zoom": "1.0",                  
            "disable-smart-shrinking": "",  
            "no-background": "",
            "enable-local-file-access": "",
            "print-media-type": ""          
        }

        if not wkhtmltopdf_path:
            raise FileNotFoundError(
            "wkhtmltopdf is not installed or not available in PATH."
            )

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

        # Passing `False` instead of a filename returns the raw bytes
        pdf_bytes = pdfkit.from_string(
            html_content,
            False,
            options=options,
            configuration=config,
        )

        return pdf_bytes

    except Exception as exc:
        raise RuntimeError(f"Error generating raw OD PDF: {str(exc)}") from exc


# ============================================================
# Apply Watermark (In-Memory)
# ============================================================

def add_roll_number_watermark(input_pdf_bytes: bytes, roll_number: str) -> bytes:
    """
    Takes raw PDF bytes, applies a staggered watermark behind it in memory,
    and returns the finalized PDF bytes.
    """
    try:
        # 1. Generate Watermark in memory buffer
        watermark_buffer = io.BytesIO()
        c = canvas.Canvas(watermark_buffer, pagesize=A4)
        
        width, height = A4
        c.translate(width / 2, height / 2) 
        c.rotate(35) 
        
        c.setFont("Helvetica-Bold", 34)
        c.setFillAlpha(0.08) 
        c.setFillColorRGB(0, 0, 0) 
        
        x_start, x_end = -1200, 1200
        y_start, y_end = -1200, 1200
        x_step = 200  
        y_step = 50  
        
        row_count = 0
        for y in range(y_start, y_end, y_step):
            offset = (x_step / 2) if row_count % 2 != 0 else 0
            for x in range(x_start, x_end, x_step):
                c.drawCentredString(x + offset, y, roll_number)
            row_count += 1
            
        c.save()
        watermark_buffer.seek(0)
        
        # 2. Merge Layers (Original PDF ON TOP of Watermark)
        watermark_reader = PdfReader(watermark_buffer)
        watermark_page = watermark_reader.pages[0]
        
        original_reader = PdfReader(io.BytesIO(input_pdf_bytes))
        original_page = original_reader.pages[0]
        
        watermark_page.merge_page(original_page)
        
        # 3. Write final PDF to in-memory buffer
        final_buffer = io.BytesIO()
        writer = PdfWriter()
        writer.add_page(watermark_page)
        writer.write(final_buffer)
        
        return final_buffer.getvalue()

    except Exception as exc:
        raise RuntimeError(f"Error applying watermark: {str(exc)}") from exc


# ============================================================
# Master Entry Point (For Celery Worker)
# ============================================================

def create_student_od_task(
    department_name: str,
    student_name: str,
    roll_number: str,
    year: str
) -> bytes:
    """
    The main function to be called by your Celery worker.
    Returns the complete, watermarked PDF as bytes for hashing/emailing.
    """
    try:
        # Step 1: Generate letter bytes
        raw_pdf_bytes = generate_od_pdf(
            department_name=department_name,
            student_name=student_name,
            roll_number=roll_number,
            year=year
        )

        # Step 2: Apply watermark to bytes
        final_pdf_bytes = add_roll_number_watermark(
            input_pdf_bytes=raw_pdf_bytes,
            roll_number=roll_number
        )

        return final_pdf_bytes

    except Exception as exc:
        # Allows Celery to properly register the failure and traceback
        raise Exception(f"OD Generation Pipeline Failed: {str(exc)}") from exc


# ============================================================
# Local Testing 
# ============================================================

if __name__ == "__main__":
    # If run directly (not via Celery), execute the pipeline and write to disk just to verify.
    try:
        pdf_bytes = create_student_od_task(
            department_name="Computer Science and Engineering",
            student_name="Kamlesh",
            roll_number="CS2026101",
            year="3"
        )
        
        test_output_path = "devs_od_request_final.pdf"
        with open(test_output_path, "wb") as f:
            f.write(pdf_bytes)
            
    except Exception as e:
        # Locally print the error if it fails
        pass