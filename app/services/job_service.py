from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.job import GenerationJob, JobStatus, CertificateStatus
from app.models.certificate import CertificateRecord
from app.schemas.job import JobCreateRequest


def create_job(db: Session, payload: JobCreateRequest) -> GenerationJob:
    """
    Creates a new GenerationJob and associated CertificateRecord entries
    in a single atomic database transaction.
    """
    job = GenerationJob(
        event_name=payload.event_name,
        certificate_date=payload.certificate_date,
        status=JobStatus.QUEUED,
        total_count=len(payload.recipients),
        completed_count=0,
        failed_count=0,
    )
    db.add(job)
    db.flush()  # Populates job.id for foreign key assignment

    for recipient in payload.recipients:
        cert = CertificateRecord(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            course=recipient.course,
            status=CertificateStatus.PENDING,
        )
        db.add(cert)

    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: str) -> Optional[GenerationJob]:
    """Retrieves a GenerationJob by its UUID."""
    return db.query(GenerationJob).filter(GenerationJob.id == job_id).first()


def get_job_certificates(db: Session, job_id: str) -> List[CertificateRecord]:
    """Retrieves all CertificateRecord instances for a given job."""
    return (
        db.query(CertificateRecord)
        .filter(CertificateRecord.job_id == job_id)
        .order_by(CertificateRecord.created_at)
        .all()
    )


def get_certificate(db: Session, certificate_id: str) -> Optional[CertificateRecord]:
    """Retrieves a single CertificateRecord by its UUID."""
    return db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
