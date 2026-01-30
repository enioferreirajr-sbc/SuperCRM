from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.import_service import import_proposals_from_excel
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/imports", tags=["imports"])


@router.post("/proposals")
def import_proposals(
    file: UploadFile = File(...),
    validate_only: bool = False,
    session: Session = Depends(get_db),
):
    return import_proposals_from_excel(session, file, validate_only=validate_only)
