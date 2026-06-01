from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PredictRequest(BaseModel):
    location_id: int
    datetime: datetime
    event_type: Optional[str] = None

class PredictResponse(BaseModel):
    location_id: int
    predicted_level: str
    confidence: float
    predicted_occupancy_rate: float
    model_version: str