from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.job import GenerationJob, JobStatus, CertificateStatus
from app.models.certificate import CertificateRecord


def test_create_generation_job_success(client: TestClient, db_session: Session):
    """
    Test 1: Create generation job
    Verify:
    - request succeeds (status code 201)
    - job ID is returned
    - job is stored in the database
    - recipient records are created
    """
    payload = {
        "event_name": "AI Workshop 2026",
        "certificate_date": "2026-10-07",
        "recipients": [
            {
                "name": "Rahul Kumar",
                "email": "rahul@example.com",
                "course": "AI Engineering",
            },
            {
                "name": "Priya Sharma",
                "email": "priya@example.com",
                "course": "AI Engineering",
            },
        ],
    }

    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "job_id" in data
    assert data["total"] == 2
    job_id = data["job_id"]

    # Verify job is stored in the database
    job = db_session.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    assert job is not None
    assert job.event_name == "AI Workshop 2026"
    assert job.certificate_date == "2026-10-07"
    assert job.total_count == 2

    # Verify recipient records are created
    certs = (
        db_session.query(CertificateRecord)
        .filter(CertificateRecord.job_id == job_id)
        .order_by(CertificateRecord.recipient_name)
        .all()
    )
    assert len(certs) == 2
    assert certs[0].recipient_name in ["Priya Sharma", "Rahul Kumar"]
    assert certs[1].recipient_name in ["Priya Sharma", "Rahul Kumar"]


def test_job_status_and_progress(client: TestClient, db_session: Session):
    """
    Test 4: Job status and progress tracking
    Verify:
    - total count, completed count, failed count, pending count
    - overall status progression
    """
    payload = {
        "event_name": "Cloud Computing Summit",
        "certificate_date": "2026-10-07",
        "recipients": [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "course": "Cloud Architecture",
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "course": "Cloud Architecture",
            },
        ],
    }

    # When submitted via TestClient, background tasks run synchronously
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 201
    job_id = response.json()["job_id"]

    # Query status
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()

    assert status_data["job_id"] == job_id
    assert status_data["status"] == JobStatus.COMPLETED
    assert status_data["total"] == 2
    assert status_data["completed"] == 2
    assert status_data["failed"] == 0
    assert status_data["pending"] == 0
    assert status_data["completed_at"] is not None


def test_get_nonexistent_job(client: TestClient):
    """Verify that querying a nonexistent job ID returns 404."""
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_job_certificates(client: TestClient):
    """Verify listing certificates for a job."""
    payload = {
        "event_name": "Web Dev Bootcamp",
        "certificate_date": "2026-10-07",
        "recipients": [
            {"name": "Dev User", "email": "dev@example.com", "course": "Full Stack"}
        ],
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    job_id = create_resp.json()["job_id"]

    list_resp = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert list_resp.status_code == 200
    certs = list_resp.json()
    assert len(certs) == 1
    assert certs[0]["recipient_name"] == "Dev User"
    assert certs[0]["status"] == CertificateStatus.COMPLETED
    assert certs[0]["download_url"] == f"/api/v1/certificates/{certs[0]['id']}"


def test_job_lifecycle_queued_to_completed(db_session: Session):
    """
    Directly tests the job service and worker lifecycle:
    - job created with status 'queued'
    - certificates created with status 'pending'
    - worker processes job to 'completed'
    """
    from app.schemas.job import JobCreateRequest
    from app.schemas.certificate import RecipientInput
    from app.services import job_service
    from app.workers.tasks import process_bulk_job

    payload = JobCreateRequest(
        event_name="Lifecycle Event",
        certificate_date="2026-10-07",
        recipients=[
            RecipientInput(name="User A", email="a@example.com", course="Math"),
            RecipientInput(name="User B", email="b@example.com", course="Physics"),
        ],
    )

    job = job_service.create_job(db_session, payload)
    assert job.status == JobStatus.QUEUED
    assert job.total_count == 2
    assert job.completed_count == 0
    assert job.failed_count == 0

    certs = job_service.get_job_certificates(db_session, job.id)
    assert len(certs) == 2
    for c in certs:
        assert c.status == CertificateStatus.PENDING
        assert c.file_path is None

    # Now execute the worker
    process_bulk_job(job.id)

    # Re-fetch from db
    db_session.expire_all()
    updated_job = job_service.get_job(db_session, job.id)
    assert updated_job.status == JobStatus.COMPLETED
    assert updated_job.completed_count == 2
    assert updated_job.failed_count == 0

    updated_certs = job_service.get_job_certificates(db_session, job.id)
    for c in updated_certs:
        assert c.status == CertificateStatus.COMPLETED
        assert c.file_path is not None

