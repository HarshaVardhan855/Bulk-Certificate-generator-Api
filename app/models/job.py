import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class CertificateStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String(255), nullable=False)
    certificate_date = Column(String(50), nullable=False)
    status = Column(String(50), default=JobStatus.QUEUED, nullable=False, index=True)
    total_count = Column(Integer, default=0, nullable=False)
    completed_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship(
        "CertificateRecord",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="CertificateRecord.created_at",
    )
