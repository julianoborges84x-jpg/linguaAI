from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.language import Language
from app.schemas.language import LanguageOut

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("", response_model=list[LanguageOut])
def list_languages(
    q: str | None = Query(default=None, description="Search by name or ISO code"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Language)
    if q:
        like = f"%{q}%"
        query = query.filter((Language.name.ilike(like)) | (Language.iso_code.ilike(like)))
    return query.order_by(Language.name.asc()).limit(limit).all()


@router.get("/{iso_code}", response_model=LanguageOut)
def get_language(iso_code: str, db: Session = Depends(get_db)):
    lang = db.query(Language).filter(Language.iso_code == iso_code).first()
    if not lang:
        raise HTTPException(status_code=404, detail="Language not found")
    return lang
