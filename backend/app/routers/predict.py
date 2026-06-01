from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.predict_service import predict_congestion
from app.schemas.predict import PredictRequest, PredictResponse

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db)):
    try:
        return predict_congestion(db, request.location_id, request.datetime, request.event_type)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except RuntimeError as e:
        raise HTTPException(503, str(e))