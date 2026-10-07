import logging
from datetime import datetime
from app.core.database import SessionLocal
from app.models.job import GenerationJob, JobStatus, CertificateStatus
from app.models.certificate import CertificateRecord
from app.services.certificate_service import generate_certificate_pdf

logger = logging.getLogger(__name__)


def process_bulk_job(job_id: str) -> None:
    """
    Background worker task to process certificate generation for a bulk job.
    Uses its own independent database session and handles per-recipient errors
    without halting the overall job processing.
    """
    db = SessionLocal()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in background worker")
            return

        job.status = JobStatus.PROCESSING
        db.commit()

        certificates = (
            db.query(CertificateRecord)
            .filter(CertificateRecord.job_id == job_id)
            .order_by(CertificateRecord.created_at)
            .all()
        )

        for cert in certificates:
            try:
                cert.status = CertificateStatus.PROCESSING
                db.commit()

                # Generate certificate PDF
                file_path = generate_certificate_pdf(
                    certificate_id=cert.id,
                    recipient_name=cert.recipient_name,
                    course=cert.course,
                    event_name=job.event_name,
                    certificate_date=job.certificate_date,
                )

                cert.file_path = str(file_path)
                cert.status = CertificateStatus.COMPLETED
                job.completed_count += 1
                db.commit()
            except Exception as exc:
                logger.warning(
                    f"Failed to generate certificate {cert.id} for recipient '{cert.recipient_name}': {exc}"
                )
                db.rollback()
                # Re-fetch entities within the session after rollback
                cert_to_update = db.query(CertificateRecord).filter(CertificateRecord.id == cert.id).first()
                job_to_update = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

                if cert_to_update:
                    cert_to_update.status = CertificateStatus.FAILED
                    cert_to_update.error_message = str(exc)
                if job_to_update:
                    job_to_update.failed_count += 1
                db.commit()

        # Update final job state and completion timestamp
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            if job.completed_count == job.total_count and job.total_count > 0:
                job.status = JobStatus.COMPLETED
            elif job.completed_count > 0 and job.failed_count > 0:
                job.status = JobStatus.COMPLETED_WITH_ERRORS
            else:
                job.status = JobStatus.FAILED

            job.completed_at = datetime.utcnow()
            db.commit()

    except Exception as exc:
        logger.error(f"Critical error processing job {job_id}: {exc}", exc_info=True)
        db.rollback()
        try:
            job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
