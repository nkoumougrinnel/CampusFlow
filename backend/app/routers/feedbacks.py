from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.feedback_service import get_feedbacks
from app.schemas.feedback import FeedbackListResponse, FeedbackOut

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])

@router.get("", response_model=FeedbackListResponse)
def list_feedbacks(
    location_id: int = None,
    sentiment: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    total, items = get_feedbacks(db, location_id, sentiment, limit, offset)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }