from fastapi import APIRouter, Query, HTTPException
from app.db import get_db

router = APIRouter(prefix="/api/laps")


def _driver_laps(conn, year: int, rnd: int, driver: str) -> dict | None:
    """Fetch lap data and stats for a single driver in a race."""
    # Get driver info
    info = conn.execute(
        """SELECT d.full_name, d.team, d.team_color
        FROM driver_info d
        WHERE d.year = ? AND d.driver_code = ?""",
        (year, driver),
    ).fetchone()
    if not info:
        return None

    # Get laps
    rows = conn.execute(
        """SELECT lap_number, lap_time_ms, compound, is_pit_in, is_pit_out, is_accurate
        FROM laps
        WHERE year = ? AND round = ? AND session_type = 'R' AND driver = ?
        ORDER BY lap_number""",
        (year, rnd, driver),
    ).fetchall()
    if not rows:
        return None

    laps = []
    accurate_times = []
    for row in rows:
        time_sec = round(row["lap_time_ms"] / 1000, 3) if row["lap_time_ms"] else None
        is_pit = bool(row["is_pit_in"] or row["is_pit_out"])
        is_accurate = bool(row["is_accurate"])
        laps.append({
            "lap": row["lap_number"],
            "time_sec": time_sec,
            "compound": row["compound"],
            "is_pit": is_pit,
            "is_accurate": is_accurate,
        })
        if is_accurate and not is_pit and time_sec:
            accurate_times.append(time_sec)

    # Get finish position
    result = conn.execute(
        """SELECT position FROM results
        WHERE year = ? AND round = ? AND session_type = 'R' AND driver_code = ?""",
        (year, rnd, driver),
    ).fetchone()

    fastest = min(accurate_times) if accurate_times else None
    avg_pace = round(sum(accurate_times) / len(accurate_times), 3) if accurate_times else None

    return {
        "code": driver,
        "name": info["full_name"],
        "team": info["team"],
        "team_color": f"#{info['team_color']}",
        "laps": laps,
        "stats": {
            "fastest_lap": fastest,
            "avg_pace": avg_pace,
            "finish_position": result["position"] if result else None,
        },
    }


@router.get("/compare")
def compare_laps(
    year: int = Query(...),
    rnd: int = Query(..., alias="round"),
    d1: str = Query(...),
    d2: str = Query(...),
):
    conn = get_db()
    try:
        driver1 = _driver_laps(conn, year, rnd, d1)
        if not driver1:
            raise HTTPException(404, f"Driver {d1} not found in {year} round {rnd}")
        driver2 = _driver_laps(conn, year, rnd, d2)
        if not driver2:
            raise HTTPException(404, f"Driver {d2} not found in {year} round {rnd}")
        return {"driver1": driver1, "driver2": driver2}
    finally:
        conn.close()
