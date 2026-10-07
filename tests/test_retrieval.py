from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import app.workers.tasks as worker_module

original_generate_pdf = worker_module.generate_certificate_pdf


def test_certificate_retrieval_success_and_failures(client: TestClient, db_session: Session):
    """
    Test 6: Certificate retrieval
    Verify:
    - completed certificate can be retrieved
    - response is PDF
    - nonexistent certificate returns 404
    - failed certificate cannot be downloaded as if it were successful
    """

    def mock_generate_pdf(certificate_id, recipient_name, course, event_name, certificate_date, **kwargs):
        if recipient_name == "Broken Recipient":
            raise ValueError("Invalid layout parameter")
        return original_generate_pdf(
            certificate_id, recipient_name, course, event_name, certificate_date, **kwargs
        )

    payload = {
        "event_name": "API Design 101",
        "certificate_date": "2026-10-07",
        "recipients": [
            {
                "name": "Successful Recipient",
                "email": "good@example.com",
                "course": "REST APIs",
            },
            {
                "name": "Broken Recipient",
                "email": "bad@example.com",
                "course": "REST APIs",
            },
        ],
    }

    with patch("app.workers.tasks.generate_certificate_pdf", side_effect=mock_generate_pdf):
        create_resp = client.post("/api/v1/jobs", json=payload)
        assert create_resp.status_code == 201
        job_id = create_resp.json()["job_id"]

    # Get certificates list
    certs_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert certs_resp.status_code == 200
    certs_data = certs_resp.json()

    succ_cert = next(c for c in certs_data if c["recipient_name"] == "Successful Recipient")
    fail_cert = next(c for c in certs_data if c["recipient_name"] == "Broken Recipient")

    # 1. Retrieve completed certificate
    dl_resp = client.get(f"/api/v1/certificates/{succ_cert['id']}")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert dl_resp.content.startswith(b"%PDF-")

    # 2. Attempt download of failed certificate -> must fail with 400
    fail_dl_resp = client.get(f"/api/v1/certificates/{fail_cert['id']}")
    assert fail_dl_resp.status_code == 400
    assert "generation failed" in fail_dl_resp.json()["detail"].lower()

    # 3. Nonexistent certificate -> 404
    missing_resp = client.get("/api/v1/certificates/00000000-0000-0000-0000-000000000000")
    assert missing_resp.status_code == 404
    assert "not found" in missing_resp.json()["detail"].lower()
