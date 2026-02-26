from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_compare_laps_success():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    assert r.status_code == 200
    data = r.json()
    assert "driver1" in data
    assert "driver2" in data


def test_compare_laps_driver_fields():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    d1 = r.json()["driver1"]
    assert d1["code"] == "VER"
    assert d1["name"] == "Max Verstappen"
    assert d1["team_color"].startswith("#")
    assert len(d1["laps"]) > 0


def test_compare_laps_time_in_seconds():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    d1 = r.json()["driver1"]
    # Lap times should be in seconds (roughly 80-120s for F1)
    clean_laps = [l for l in d1["laps"] if l["is_accurate"] and not l["is_pit"] and l["time_sec"]]
    assert len(clean_laps) > 0
    for lap in clean_laps:
        assert 60 < lap["time_sec"] < 200


def test_compare_laps_stats():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    stats = r.json()["driver1"]["stats"]
    assert "fastest_lap" in stats
    assert "avg_pace" in stats
    assert "finish_position" in stats
    assert stats["fastest_lap"] is not None
    assert stats["avg_pace"] > stats["fastest_lap"]
    assert stats["finish_position"] == 1  # VER won Bahrain 2024


def test_compare_laps_pit_flags():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    d1 = r.json()["driver1"]
    pit_laps = [l for l in d1["laps"] if l["is_pit"]]
    # VER should have at least 1 pit stop
    assert len(pit_laps) > 0


def test_compare_laps_lap_fields():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "HAM"})
    lap = r.json()["driver1"]["laps"][0]
    assert "lap" in lap
    assert "time_sec" in lap
    assert "compound" in lap
    assert "is_pit" in lap
    assert "is_accurate" in lap


def test_compare_laps_invalid_driver():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER", "d2": "XXX"})
    assert r.status_code == 404


def test_compare_laps_missing_params():
    r = client.get("/api/laps/compare", params={"year": 2024, "round": 1, "d1": "VER"})
    assert r.status_code == 422
