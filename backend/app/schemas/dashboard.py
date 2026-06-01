from pydantic import BaseModel
from typing import List, Dict

class DashboardStats(BaseModel):
    top_locations: List[dict]  # [{id, name, avg_congestion}]
    peak_hours: List[dict]  # [{hour, avg_count}]
    avg_congestion_by_day: List[dict]  # [{day, level}]
    feedback_summary: Dict[str, int]  # {positive, negative, neutral}
    total_flux: int