import pytest
from app.services.location_service import get_all_locations
from app.services.congestion_service import get_congestion
from app.services.path_service import find_path, build_graph
from app.services.flux_service import get_live_flux

def test_get_all_locations(db_session, sample_locations):
    locs = get_all_locations(db_session, active_only=True)
    assert len(locs) == 2
    locs_all = get_all_locations(db_session, active_only=False)
    assert len(locs_all) == 3

def test_get_congestion_service(db_session, sample_locations, sample_flux):
    cong = get_congestion(db_session)
    assert len(cong) == 2
    for c in cong:
        assert "level" in c
        assert c["occupancy_rate"] >= 0

def test_build_graph(db_session, sample_locations):
    G = build_graph(db_session)
    nodes = list(G.nodes)
    assert len(nodes) == 2  # seulement les actifs
    assert G.has_edge(sample_locations[0].id, sample_locations[1].id)

def test_find_path_service(db_session, sample_locations):
    from_id = sample_locations[0].id
    to_id = sample_locations[1].id
    path_data = find_path(db_session, from_id, to_id, avoid_congestion=False, congestion_service=None)
    assert path_data is not None
    assert path_data["path"][0] == from_id
    assert path_data["path"][-1] == to_id
    assert path_data["total_distance"] > 0

def test_live_flux_service(db_session, sample_flux):
    flux = get_live_flux(db_session, window_minutes=60)
    assert len(flux) >= 2
    for f in flux:
        assert "net_flow" in f