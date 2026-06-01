from pydantic import BaseModel
from typing import Optional

class LocationBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    type: str
    capacity: int
    description: Optional[str] = None
    is_active: bool = True

class LocationOut(LocationBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True