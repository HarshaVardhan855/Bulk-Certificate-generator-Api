from pathlib import Path
from app.services.certificate_service import generate_certificate_pdf


def test_certificate_pdf_generation(tmp_path: Path):
    """
    Test 3: Certificate generation
    Verify:
    - certificate generator runs
    - PDF is created
    - generated file exists
    - file has valid PDF header/signature (%PDF-)
    """
    certificate_id = "test-cert-unique-001"
    recipient_name = "Jane Doe"
    course = "Full Stack Web Development"
    event_name = "Tech Academy 2026"
    certificate_date = "2026-10-07"

    output_path = generate_certificate_pdf(
        certificate_id=certificate_id,
        recipient_name=recipient_name,
        course=course,
        event_name=event_name,
        certificate_date=certificate_date,
        output_dir=tmp_path,
    )

    # Verify file existence and path
    assert output_path.exists()
    assert output_path.is_file()
    assert output_path.name == f"certificate_{certificate_id}.pdf"
    assert output_path.stat().st_size > 500  # Non-trivial size

    # Verify PDF signature (%PDF-)
    with open(output_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-", f"Expected %PDF- header, got {header!r}"
