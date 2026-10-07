import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.job import CertificateStatus


class CertificateRecord(Base):
    __tablename__ = "certificate_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    course = Column(String(255), nullable=False)
    status = Column(String(50), default=CertificateStatus.PENDING, nullable=False, index=True)
    file_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("GenerationJob", back_populates="certificates")
