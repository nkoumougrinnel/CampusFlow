from sqlalchemy.orm import Session
from app.database.models import Location, Flux, Feedback, Schedule
from datetime import datetime, timedelta
import random

def seed_database(db: Session):
    # Vider (optionnel)
    db.query(Flux).delete()
    db.query(Feedback).delete()
    db.query(Schedule).delete()
    db.query(Location).delete()

    # Bâtiments
    buildings = [
        ("Bât. A - Amphithéâtre", 48.8566, 2.3522, "amphi", 300),
        ("Bât. B - Sciences", 48.8570, 2.3530, "labo", 150),
        ("Bât. C - Administration", 48.8560, 2.3515, "admin", 50),
        ("Bât. D - Bibliothèque", 48.8575, 2.3527, "bibliotheque", 200),
        ("Bât. E - Resto U", 48.8555, 2.3525, "restaurant", 250),
    ]
    for name, lat, lon, typ, cap in buildings:
        loc = Location(name=name, latitude=lat, longitude=lon, type=typ, capacity=cap, is_active=True)
        db.add(loc)
    db.commit()

    locations = db.query(Location).all()
    now = datetime.utcnow()
    # Flux simulé sur 7 jours
    for loc in locations:
        for delta_h in range(-168, 0, 1):  # dernières 168h
            ts = now + timedelta(hours=delta_h)
            hour = ts.hour
            base = 50 if 8 <= hour <= 18 else 10
            if loc.type == "amphi":
                base = 120 if 9 <= hour <= 12 else 20
            count = int(base + random.gauss(0, 15))
            count = max(0, min(count, loc.capacity))
            entries = random.randint(0, count)
            exits = random.randint(0, count - entries) if count-entries>0 else 0
            flux = Flux(location_id=loc.id, timestamp=ts, entries=entries, exits=exits, count=count)
            db.add(flux)

    # Feedbacks
    for _ in range(50):
        fb = Feedback(
            location_id=random.choice(locations).id,
            content="Texte exemple",
            rating=random.randint(1,5),
            sentiment=random.choice(["positive","negative","neutral"]),
            created_at=now - timedelta(days=random.randint(0,30)),
            student_hash=hash(str(random.random()))
        )
        db.add(fb)
    db.commit()