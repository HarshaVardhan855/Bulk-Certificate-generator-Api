from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.job import CertificateStatus
from app.services import job_service

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get(
    "/{certificate_id}",
    summary="Download generated certificate PDF",
    description="Returns the PDF file for a successfully generated certificate.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "The generated PDF certificate file.",
        },
        400: {"description": "Certificate generation failed or is incomplete."},
        404: {"description": "Certificate record or PDF file not found."},
    },
)
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    cert = job_service.get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' not found",
        )

    if cert.status == CertificateStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate generation failed: {cert.error_message or 'Unknown error'}",
        )

    if cert.status != CertificateStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate is not ready yet (current status: {cert.status})",
        )

    if not cert.file_path or not Path(cert.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate PDF file is missing from the server storage",
        )

    safe_filename = f"certificate_{cert.id}.pdf"
    return FileResponse(
        path=cert.file_path,
        media_type="application/pdf",
        filename=safe_filename,
    )
