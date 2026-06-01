from datetime import datetime

def test_predict_endpoint(client, sample_locations, monkeypatch):
    # Simuler le modèle chargé
    from app.services import predict_service
    class MockModel:
        def predict(self, X):
            return [2]  # high
        def predict_proba(self, X):
            return [[0.1, 0.2, 0.6, 0.1]]
    monkeypatch.setattr(predict_service, "load_model", lambda: MockModel())
    payload = {
        "location_id": sample_locations[0].id,
        "datetime": datetime.utcnow().isoformat(),
        "event_type": "cours"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_level"] == "high"
    assert 0 <= data["confidence"] <= 1
    assert "model_version" in data

def test_predict_location_not_found(client):
    payload = {
        "location_id": 999,
        "datetime": datetime.utcnow().isoformat()
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 404