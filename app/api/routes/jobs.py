from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.job import JobCreateRequest, JobCreateResponse, JobStatusResponse
from app.schemas.certificate import CertificateResponse
from app.services import job_service
from app.workers.tasks import process_bulk_job

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a bulk certificate generation job",
    description="Submits a list of recipients for bulk certificate generation and triggers background processing.",
)
def create_generation_job(
    payload: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> JobCreateResponse:
    job = job_service.create_job(db, payload)
    background_tasks.add_task(process_bulk_job, job.id)

    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        total=job.total_count,
    )


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get job status and progress",
    description="Returns the current processing status, total, completed, failed, and pending certificate counts.",
)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
) -> JobStatusResponse:
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found",
        )

    pending_count = max(0, job.total_count - (job.completed_count + job.failed_count))

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        total=job.total_count,
        completed=job.completed_count,
        failed=job.failed_count,
        pending=pending_count,
        event_name=job.event_name,
        certificate_date=job.certificate_date,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get(
    "/{job_id}/certificates",
    response_model=List[CertificateResponse],
    summary="List certificates for a job",
    description="Retrieves the certificate generation records and download links for a specific job.",
)
def list_job_certificates(
    job_id: str,
    db: Session = Depends(get_db),
) -> List[CertificateResponse]:
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found",
        )

    certificates = job_service.get_job_certificates(db, job_id)
    response: List[CertificateResponse] = []
    for cert in certificates:
        download_url = f"/api/v1/certificates/{cert.id}" if cert.status == "completed" else None
        response.append(
            CertificateResponse(
                id=cert.id,
                job_id=cert.job_id,
                recipient_name=cert.recipient_name,
                recipient_email=cert.recipient_email,
                course=cert.course,
                status=cert.status,
                file_path=cert.file_path,
                error_message=cert.error_message,
                created_at=cert.created_at,
                download_url=download_url,
            )
        )
    return response
