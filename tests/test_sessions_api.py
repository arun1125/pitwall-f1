from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_years():
    r = client.get("/api/years")
    assert r.status_code == 200
    years = r.json()
    assert isinstance(years, list)
    assert len(years) > 0
    # Should be descending
    assert years == sorted(years, reverse=True)
    assert 2024 in years


def test_get_events():
    r = client.get("/api/events", params={"year": 2024})
    assert r.status_code == 200
    events = r.json()
    assert len(events) > 0
    first = events[0]
    assert "round" in first
    assert "name" in first
    assert "country" in first
    assert "date" in first
    # Round 1 should be first
    assert first["round"] == 1


def test_get_events_invalid_year():
    r = client.get("/api/events", params={"year": 1950})
    assert r.status_code == 200
    assert r.json() == []


def test_get_events_missing_param():
    r = client.get("/api/events")
    assert r.status_code == 422


def test_get_drivers():
    r = client.get("/api/drivers", params={"year": 2024, "round": 1})
    assert r.status_code == 200
    drivers = r.json()
    assert len(drivers) == 20  # Full grid
    first = drivers[0]
    assert "driver_code" in first
    assert "full_name" in first
    assert "team" in first
    assert "team_color" in first
    # Team color should have # prefix
    assert first["team_color"].startswith("#")


def test_get_drivers_known_driver():
    r = client.get("/api/drivers", params={"year": 2024, "round": 1})
    drivers = r.json()
    codes = [d["driver_code"] for d in drivers]
    assert "VER" in codes
    assert "HAM" in codes


def test_get_drivers_missing_params():
    r = client.get("/api/drivers", params={"year": 2024})
    assert r.status_code == 422
    r = client.get("/api/drivers")
    assert r.status_code == 422


def test_get_drivers_invalid_round():
    r = client.get("/api/drivers", params={"year": 2024, "round": 999})
    assert r.status_code == 200
    assert r.json() == []
