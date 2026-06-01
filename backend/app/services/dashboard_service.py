from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Flux, Feedback, Location
from datetime import datetime, timedelta

def get_dashboard_stats(db: Session, period: str = "week"):
    # Période
    end = datetime.utcnow()
    if period == "day":
        start = end - timedelta(days=1)
    elif period == "week":
        start = end - timedelta(days=7)
    else:  # month
        start = end - timedelta(days=30)

    # Top locations (moyenne de congestion sur la période)
    top_locs = db.query(
        Flux.location_id,
        Location.name,
        func.avg(Flux.count / Location.capacity).label("congestion_rate")
    ).join(Location, Location.id == Flux.location_id)\
     .filter(Flux.timestamp >= start)\
     .group_by(Flux.location_id, Location.name)\
     .order_by(desc("congestion_rate")).limit(5).all()
    top_locations = [{"id": t[0], "name": t[1], "avg_congestion": float(t[2])} for t in top_locs]

    # Heures de pointe
    peak_hours = db.query(
        func.extract('hour', Flux.timestamp).label("hour"),
        func.avg(Flux.count).label("avg_count")
    ).filter(Flux.timestamp >= start)\
     .group_by("hour").order_by(desc("avg_count")).limit(5).all()
    peak_hours = [{"hour": int(h), "avg_count": int(cnt)} for h, cnt in peak_hours]

    # Congestion par jour de semaine
    avg_by_day = db.query(
        func.extract('dow', Flux.timestamp).label("day_num"),
        func.avg(Flux.count / Location.capacity).label("avg_rate")
    ).join(Location, Location.id == Flux.location_id)\
     .filter(Flux.timestamp >= start)\
     .group_by("day_num").all()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    avg_congestion_by_day = [{"day": days[int(d)], "level": "medium" if rate>0.5 else "low"} for d, rate in avg_by_day]

    # Feedback summary
    feedback_summary = db.query(
        Feedback.sentiment,
        func.count().label("cnt")
    ).filter(Feedback.created_at >= start)\
     .group_by(Feedback.sentiment).all()
    summary = {s: 0 for s in ["positive", "negative", "neutral"]}
    for sent, cnt in feedback_summary:
        summary[sent] = cnt

    total_flux = db.query(func.sum(Flux.entries)).filter(Flux.timestamp >= start).scalar() or 0

    return {
        "top_locations": top_locations,
        "peak_hours": peak_hours,
        "avg_congestion_by_day": avg_congestion_by_day,
        "feedback_summary": summary,
        "total_flux": total_flux
    }