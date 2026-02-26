from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_championship_drivers_2024():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    assert r.status_code == 200
    data = r.json()
    drivers = data["drivers"]
    assert len(drivers) > 0
    first = drivers[0]
    assert "code" in first
    assert "name" in first
    assert "team" in first
    assert "team_color" in first
    assert "final_position" in first
    assert "rounds" in first
    assert len(first["rounds"]) > 0


def test_championship_drivers_sorted_by_position():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    drivers = r.json()["drivers"]
    positions = [d["final_position"] for d in drivers]
    assert positions == sorted(positions)


def test_championship_ver_position_1_in_2024():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    drivers = r.json()["drivers"]
    ver = next(d for d in drivers if d["code"] == "VER")
    assert ver["final_position"] == 1
    assert ver["name"] == "Max Verstappen"


def test_championship_round_data_has_race_names():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    drivers = r.json()["drivers"]
    first_driver = drivers[0]
    round1 = first_driver["rounds"][0]
    assert "round" in round1
    assert "race_name" in round1
    assert "round_points" in round1
    assert "cumulative_points" in round1
    assert round1["round"] == 1
    assert isinstance(round1["race_name"], str)
    assert len(round1["race_name"]) > 0


def test_championship_cumulative_points_increase():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    drivers = r.json()["drivers"]
    ver = next(d for d in drivers if d["code"] == "VER")
    cumulative = [r["cumulative_points"] for r in ver["rounds"]]
    # Cumulative points should be non-decreasing
    for i in range(1, len(cumulative)):
        assert cumulative[i] >= cumulative[i - 1]


def test_championship_team_color_has_hash():
    r = client.get("/api/championship/drivers", params={"year": 2024})
    drivers = r.json()["drivers"]
    for d in drivers:
        assert d["team_color"].startswith("#"), f"{d['code']} team_color missing # prefix"


def test_championship_invalid_year():
    r = client.get("/api/championship/drivers", params={"year": 1950})
    assert r.status_code == 200
    assert r.json() == {"drivers": []}


def test_championship_missing_year():
    r = client.get("/api/championship/drivers")
    assert r.status_code == 422
