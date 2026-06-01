from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.utils.redis_client import redis_client
from app.database.models import Flux, Location
import json

def get_congestion(db: Session, location_id: int = None):
    # Essayer Redis d'abord
    if location_id:
        cached = redis_client.get(f"congestion:{location_id}")
        if cached:
            return [json.loads(cached)]
    else:
        keys = redis_client.keys("congestion:*")
        if keys:
            return [json.loads(redis_client.get(k)) for k in keys]

    # Sinon calcul depuis PostgreSQL
    last_minute = datetime.utcnow() - timedelta(minutes=1)
    query = db.query(
        Flux.location_id,
        func.avg(Flux.count).label("avg_count"),
        func.max(Flux.count).label("max_count")
    ).filter(Flux.timestamp >= last_minute)

    if location_id:
        query = query.filter(Flux.location_id == location_id)

    results = query.group_by(Flux.location_id).all()

    congestion_data = []
    for loc_id, avg_count, max_count in results:
        location = db.query(Location).filter(Location.id == loc_id).first()
        if not location:
            continue
        occupancy_rate = min(avg_count / location.capacity, 1.0)
        if occupancy_rate < 0.3:
            level = "low"
        elif occupancy_rate < 0.6:
            level = "medium"
        elif occupancy_rate < 0.85:
            level = "high"
        else:
            level = "critical"

        data = {
            "location_id": loc_id,
            "level": level,
            "occupancy_rate": round(occupancy_rate, 2),
            "current_count": int(avg_count),
            "updated_at": datetime.utcnow().isoformat()
        }
        congestion_data.append(data)
        redis_client.setex(f"congestion:{loc_id}", 60, json.dumps(data))

    return congestion_data