import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://campusflow:securepass@localhost:5432/campusflow")

def train():
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql("SELECT * FROM flux", engine)
    df['weekday'] = pd.to_datetime(df['timestamp']).dt.weekday
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    # Définir niveau de congestion basé sur count / capacity (joindre locations)
    locs = pd.read_sql("SELECT id, capacity FROM locations", engine)
    df = df.merge(locs, left_on='location_id', right_on='id')
    df['occupancy_rate'] = df['count'] / df['capacity']
    df['level'] = pd.cut(df['occupancy_rate'], bins=[0,0.3,0.6,0.85,1.0], labels=[0,1,2,3])
    features = ['location_id', 'weekday', 'hour']
    X = df[features]
    y = df['level']
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    joblib.dump(model, "models/congestion_rf.pkl")
    print("Model saved to models/congestion_rf.pkl")

if __name__ == "__main__":
    train()