from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.certificate import RecipientInput


class JobCreateRequest(BaseModel):
    event_name: str = Field(..., description="Name of the event or program")
    certificate_date: str = Field(..., description="Date of certificate issuance (YYYY-MM-DD)")
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of certificate recipients")

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("event_name cannot be empty or whitespace-only")
        return trimmed

    @field_validator("certificate_date")
    @classmethod
    def validate_certificate_date(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("certificate_date cannot be empty")
        try:
            # Validates standard YYYY-MM-DD format
            date.fromisoformat(trimmed)
        except ValueError:
            raise ValueError("certificate_date must be in valid YYYY-MM-DD format")
        return trimmed

    @field_validator("recipients")
    @classmethod
    def validate_recipients_non_empty(cls, value: List[RecipientInput]) -> List[RecipientInput]:
        if not value:
            raise ValueError("recipients list cannot be empty")
        return value


class JobCreateResponse(BaseModel):
    job_id: str
    status: str
    total: int


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total: int
    completed: int
    failed: int
    pending: int
    event_name: Optional[str] = None
    certificate_date: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
