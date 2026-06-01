from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.congestion_service import get_congestion
from app.schemas.congestion import CongestionResponse

router = APIRouter(prefix="/congestion", tags=["congestion"])

@router.get("", response_model=list[CongestionResponse])
def get_congestion_endpoint(location_id: int = None, db: Session = Depends(get_db)):
    try:
        result = get_congestion(db, location_id)
        if location_id and not result:
            raise HTTPException(404, "Location not found")
        return result
    except Exception as e:
        raise HTTPException(503, f"Redis unavailable or error: {str(e)}")