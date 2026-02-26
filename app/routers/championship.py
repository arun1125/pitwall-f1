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


@router.get("/constructors")
def get_championship_constructors(year: int = Query(...)):
    conn = get_db()

    rows = conn.execute(
        """SELECT cp.team, cp.team_color, cp.round, e.name AS race_name,
                  SUM(cp.round_points) AS round_points,
                  SUM(cp.cumulative_points) AS cumulative_points
           FROM championship_progression cp
           JOIN events e ON cp.year = e.year AND cp.round = e.round
           WHERE cp.year = ?
           GROUP BY cp.team, cp.round
           ORDER BY cp.round""",
        (year,),
    ).fetchall()
    conn.close()

    if not rows:
        return {"constructors": []}

    # Group by team
    teams_map = {}
    for row in rows:
        team = row["team"]
        if team not in teams_map:
            teams_map[team] = {
                "team": team,
                "team_color": row["team_color"],
                "rounds": [],
            }
        teams_map[team]["rounds"].append({
            "round": row["round"],
            "race_name": row["race_name"],
            "round_points": row["round_points"],
            "cumulative_points": row["cumulative_points"],
        })

    # Sort by final cumulative points (descending)
    constructors = sorted(
        teams_map.values(),
        key=lambda t: t["rounds"][-1]["cumulative_points"],
        reverse=True,
    )
    return {"constructors": constructors}
