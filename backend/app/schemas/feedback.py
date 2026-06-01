from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FeedbackBase(BaseModel):
    location_id: int
    content: str
    rating: int  # 1-5
    student_hash: Optional[str] = None

class FeedbackOut(FeedbackBase):
    id: int
    sentiment: str
    created_at: datetime

    class Config:
        from_attributes = True

class FeedbackListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[FeedbackOut]