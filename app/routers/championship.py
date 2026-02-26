from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api/championship")


@router.get("/drivers")
def get_championship_drivers(year: int = Query(...)):
    conn = get_db()

    # Get all championship progression data joined with event names
    rows = conn.execute(
        """SELECT cp.driver_code, cp.driver_name, cp.team, cp.team_color,
                  cp.round, e.name AS race_name, cp.round_points, cp.cumulative_points,
                  cp.position
           FROM championship_progression cp
           JOIN events e ON cp.year = e.year AND cp.round = e.round
           WHERE cp.year = ?
           ORDER BY cp.round, cp.position""",
        (year,),
    ).fetchall()
    conn.close()

    if not rows:
        return {"drivers": []}

    # Group by driver
    drivers_map = {}
    for row in rows:
        code = row["driver_code"]
        if code not in drivers_map:
            drivers_map[code] = {
                "code": code,
                "name": row["driver_name"],
                "team": row["team"],
                "team_color": row["team_color"],
                "final_position": None,
                "rounds": [],
            }
        drivers_map[code]["rounds"].append({
            "round": row["round"],
            "race_name": row["race_name"],
            "round_points": row["round_points"],
            "cumulative_points": row["cumulative_points"],
        })
        # Track final position (last round's position)
        drivers_map[code]["final_position"] = row["position"]

    # Sort by final position
    drivers = sorted(drivers_map.values(), key=lambda d: d["final_position"])
    return {"drivers": drivers}
