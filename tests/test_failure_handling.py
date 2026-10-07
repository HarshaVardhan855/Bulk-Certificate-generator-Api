from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.job import JobStatus, CertificateStatus
import app.workers.tasks as worker_module

original_generate_pdf = worker_module.generate_certificate_pdf


def test_individual_certificate_failure_isolation(client: TestClient, db_session: Session):
    """
    Test 5: Individual certificate failure
    Create a bulk job containing 3 recipients.
    Force/mock the 2nd recipient's certificate generation to fail.
    Verify:
    - recipient 1 -> completed
    - recipient 2 -> failed with error details recorded
    - recipient 3 -> completed
    - Failure of recipient 2 does NOT prevent recipient 3 from processing.
    - Job overall status -> completed_with_errors (total=3, completed=2, failed=1)
    """

    def mock_generate_pdf(certificate_id, recipient_name, course, event_name, certificate_date, **kwargs):
        if recipient_name == "Failing Recipient":
            raise RuntimeError("Simulated PDF generation error for testing")
        return original_generate_pdf(
            certificate_id, recipient_name, course, event_name, certificate_date, **kwargs
        )

    payload = {
        "event_name": "DevSecOps Workshop 2026",
        "certificate_date": "2026-10-07",
        "recipients": [
            {
                "name": "Recipient One",
                "email": "recipient1@example.com",
                "course": "DevSecOps",
            },
            {
                "name": "Failing Recipient",
                "email": "recipient2@example.com",
                "course": "DevSecOps",
            },
            {
                "name": "Recipient Three",
                "email": "recipient3@example.com",
                "course": "DevSecOps",
            },
        ],
    }

    with patch("app.workers.tasks.generate_certificate_pdf", side_effect=mock_generate_pdf):
        response = client.post("/api/v1/jobs", json=payload)
        assert response.status_code == 201
        job_id = response.json()["job_id"]

    # Verify job status
    job_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert job_resp.status_code == 200
    job_data = job_resp.json()

    assert job_data["status"] == JobStatus.COMPLETED_WITH_ERRORS
    assert job_data["total"] == 3
    assert job_data["completed"] == 2
    assert job_data["failed"] == 1
    assert job_data["pending"] == 0

    # Verify individual certificate statuses
    certs_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert certs_resp.status_code == 200
    certs_data = certs_resp.json()
    assert len(certs_data) == 3

    # Map by recipient name
    cert_map = {c["recipient_name"]: c for c in certs_data}

    # Recipient 1 must be completed
    assert cert_map["Recipient One"]["status"] == CertificateStatus.COMPLETED
    assert cert_map["Recipient One"]["file_path"] is not None
    assert cert_map["Recipient One"]["error_message"] is None

    # Recipient 2 must be failed
    assert cert_map["Failing Recipient"]["status"] == CertificateStatus.FAILED
    assert cert_map["Failing Recipient"]["file_path"] is None
    assert "Simulated PDF generation error" in cert_map["Failing Recipient"]["error_message"]

    # Recipient 3 must be completed
    assert cert_map["Recipient Three"]["status"] == CertificateStatus.COMPLETED
    assert cert_map["Recipient Three"]["file_path"] is not None
    assert cert_map["Recipient Three"]["error_message"] is None
