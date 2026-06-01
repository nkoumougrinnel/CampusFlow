def test_live_flux(client, sample_flux):
    response = client.get("/flux/live?window=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Au moins un flux par bâtiment actif
    assert len(data) >= 2
    assert "entries" in data[0]
    assert "net_flow" in data[0]

def test_flux_history(client, sample_locations, sample_flux):
    loc_id = sample_locations[0].id
    response = client.get(f"/flux/history/{loc_id}?granularity=hour")
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == loc_id
    assert "data" in data
    assert isinstance(data["data"], list)