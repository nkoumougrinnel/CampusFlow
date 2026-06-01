from sqlalchemy.orm import Session
from app.database.models import Location

def get_all_locations(db: Session, type_filter: str = None, active_only: bool = True):
    query = db.query(Location)
    if active_only:
        query = query.filter(Location.is_active == True)
    if type_filter:
        query = query.filter(Location.type == type_filter)
    return query.all()