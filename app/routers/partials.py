from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.db import get_db

router = APIRouter(prefix="/partials")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")


@router.get("/events", response_class=HTMLResponse)
def events_partial(request: Request, year: int = Query(...)):
    conn = get_db()
    rows = conn.execute(
        "SELECT round, name FROM events WHERE year = ? ORDER BY round",
        (year,),
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(
        "partials/events.html",
        {"request": request, "events": [dict(r) for r in rows]},
    )


@router.get("/drivers", response_class=HTMLResponse)
def drivers_partial(request: Request, year: int = Query(...), round: int = Query(...)):
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
    return templates.TemplateResponse(
        "partials/drivers.html",
        {"request": request, "drivers": [dict(r) for r in rows]},
    )
