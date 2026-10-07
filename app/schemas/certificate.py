from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RecipientInput(BaseModel):
    name: str = Field(..., description="Recipient's full name")
    email: EmailStr = Field(..., description="Recipient's valid email address")
    course: str = Field(..., description="Course or program completed")

    @field_validator("name", "course")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace-only")
        return trimmed


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    recipient_name: str
    recipient_email: str
    course: str
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    download_url: Optional[str] = None
