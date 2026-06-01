from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class CongestionLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class CongestionResponse(BaseModel):
    location_id: int
    level: CongestionLevel
    occupancy_rate: float  # 0..1
    current_count: int
    updated_at: datetime