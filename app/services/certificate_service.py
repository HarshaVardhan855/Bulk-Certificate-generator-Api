from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from app.core.config import GENERATED_DIR


def generate_certificate_pdf(
    certificate_id: str,
    recipient_name: str,
    course: str,
    event_name: str,
    certificate_date: str,
    output_dir: Path = GENERATED_DIR,
) -> Path:
    """
    Generates a professional, print-ready PDF certificate using ReportLab.
    Saves the file with a deterministic, safe filename.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"certificate_{certificate_id}.pdf"

    # Use landscape letter: 792 x 612 pt
    page_width, page_height = landscape(letter)
    c = canvas.Canvas(str(file_path), pagesize=landscape(letter))

    # --- Background & Borders ---
    # Outer background - subtle off-white/ivory
    c.setFillColor(colors.HexColor("#FAF9F6"))
    c.rect(0, 0, page_width, page_height, stroke=0, fill=1)

    # Outer decorative border (Deep Navy)
    c.setStrokeColor(colors.HexColor("#1A2B4C"))
    c.setLineWidth(5)
    c.rect(24, 24, page_width - 48, page_height - 48)

    # Inner decorative border (Warm Gold)
    c.setStrokeColor(colors.HexColor("#C89B3C"))
    c.setLineWidth(1.5)
    c.rect(32, 32, page_width - 64, page_height - 64)

    # Corner accents
    corner_size = 18
    c.setStrokeColor(colors.HexColor("#C89B3C"))
    c.setLineWidth(2)
    # Top-left corner
    c.line(40, page_height - 40, 40 + corner_size, page_height - 40)
    c.line(40, page_height - 40, 40, page_height - 40 - corner_size)
    # Top-right corner
    c.line(page_width - 40, page_height - 40, page_width - 40 - corner_size, page_height - 40)
    c.line(page_width - 40, page_height - 40, page_width, page_height - 40 - corner_size)
    # Bottom-left corner
    c.line(40, 40, 40 + corner_size, 40)
    c.line(40, 40, 40, 40 + corner_size)
    # Bottom-right corner
    c.line(page_width - 40, 40, page_width - 40 - corner_size, 40)
    c.line(page_width - 40, 40, page_width - 40 - corner_size, 40)

    # --- Header / Title ---
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#1A2B4C"))
    c.drawCentredString(page_width / 2.0, page_height - 100, "CERTIFICATE OF COMPLETION")

    # Gold decorative separator line
    c.setStrokeColor(colors.HexColor("#C89B3C"))
    c.setLineWidth(2)
    c.line(page_width / 2.0 - 140, page_height - 116, page_width / 2.0 + 140, page_height - 116)

    # --- Subtitle ---
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(page_width / 2.0, page_height - 150, "THIS IS PROUDLY PRESENTED TO")

    # --- Recipient Name ---
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.HexColor("#1A2B4C"))
    c.drawCentredString(page_width / 2.0, page_height - 200, recipient_name)

    # Underline under recipient name
    name_width = c.stringWidth(recipient_name, "Helvetica-Bold", 30)
    underline_half = max(name_width / 2.0 + 20, 160)
    c.setStrokeColor(colors.HexColor("#C89B3C"))
    c.setLineWidth(1)
    c.line(page_width / 2.0 - underline_half, page_height - 212, page_width / 2.0 + underline_half, page_height - 212)

    # --- Description Text ---
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(page_width / 2.0, page_height - 250, "for successfully completing the course")

    # --- Course Name ---
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#2C3E50"))
    c.drawCentredString(page_width / 2.0, page_height - 290, course)

    # --- Event Name ---
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(page_width / 2.0, page_height - 330, f"as part of {event_name}")

    # --- Footer Details ---
    # Left: Issue Date
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(60, 100, f"Date: {certificate_date}")

    # Right: Certificate ID
    c.drawRightString(page_width - 60, 100, f"ID: {certificate_id}")

    # Center signature line
    sig_x = page_width / 2.0
    c.setStrokeColor(colors.HexColor("#777777"))
    c.setLineWidth(1)
    c.line(sig_x - 90, 110, sig_x + 90, 110)
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawCentredString(sig_x, 94, "Authorized Signature")

    # Finalize and save
    c.showPage()
    c.save()

    return file_path
