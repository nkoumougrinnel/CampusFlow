def test_get_feedbacks(client, sample_feedbacks):
    response = client.get("/feedbacks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) == 2
    assert data["items"][0]["sentiment"] == "positive"

def test_get_feedbacks_filter_by_location(client, sample_locations, sample_feedbacks):
    loc_id = sample_locations[0].id
    response = client.get(f"/feedbacks?location_id={loc_id}")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["location_id"] == loc_id

def test_get_feedbacks_pagination(client, sample_feedbacks):
    response = client.get("/feedbacks?limit=1&offset=0")
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] >= 2