from pydantic import BaseModel
from datetime import datetime
from typing import List

class FluxLiveResponse(BaseModel):
    location_id: int
    entries: int
    exits: int
    net_flow: int
    timestamp: datetime

class FluxHistoryResponse(BaseModel):
    location_id: int
    period: dict  # {from, to}
    granularity: str
    data: List[dict]  # [{timestamp, count, entries, exits}]