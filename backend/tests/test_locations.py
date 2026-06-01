def test_get_locations(client, sample_locations):
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Seuls les actifs (Bat A et B) doivent être retournés
    assert len(data) == 2
    assert data[0]["name"] == "Bat A"
    assert data[0]["is_active"] == True

def test_get_locations_with_type_filter(client, sample_locations):
    response = client.get("/locations?type=amphi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "amphi"

def test_get_locations_with_active_false(client, sample_locations):
    response = client.get("/locations?active=false")
    assert response.status_code == 200
    data = response.json()
    # active=false retourne tous, y compris inactifs
    assert len(data) == 3