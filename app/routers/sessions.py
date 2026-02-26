from fastapi import APIRouter, Query
from app.db import get_db

router = APIRouter(prefix="/api")


@router.get("/years")
def get_years():
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT year FROM events ORDER BY year DESC"
    ).fetchall()
    conn.close()
    return [row["year"] for row in rows]


@router.get("/events")
def get_events(year: int = Query(...)):
    conn = get_db()
    rows = conn.execute(
        "SELECT round, name, country, date FROM events WHERE year = ? ORDER BY round",
        (year,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/drivers")
def get_drivers(year: int = Query(...), round: int = Query(...)):
    conn = get_db()
    rows = conn.execute(
        """SELECT DISTINCT r.driver_code, d.full_name, d.team, d.team_color
        FROM results r
        JOIN driver_info d ON r.driver_code = d.driver_code AND r.year = d.year
        WHERE r.year = ? AND r.round = ? AND r.session_type = 'R'
        ORDER BY r.position""",
        (year, round),
    ).fetchall()
    conn.close()
    return [
        {
            "driver_code": row["driver_code"],
            "full_name": row["full_name"],
            "team": row["team"],
            "team_color": f"#{row['team_color']}",
        }
        for row in rows
    ]
