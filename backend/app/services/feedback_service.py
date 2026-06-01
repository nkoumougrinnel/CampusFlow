from sqlalchemy.orm import Session
from app.database.models import Feedback

def get_feedbacks(db: Session, location_id: int = None, sentiment: str = None,
                  limit: int = 20, offset: int = 0):
    q = db.query(Feedback)
    if location_id:
        q = q.filter(Feedback.location_id == location_id)
    if sentiment:
        q = q.filter(Feedback.sentiment == sentiment)
    total = q.count()
    items = q.order_by(Feedback.created_at.desc()).offset(offset).limit(limit).all()
    return total, items