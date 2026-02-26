from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routers import sessions, partials
from app.db import get_db

app = FastAPI(title="Pitwall")
app.include_router(sessions.router)
app.include_router(partials.router)

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT year FROM events ORDER BY year DESC").fetchall()
    conn.close()
    years = [row["year"] for row in rows]
    return templates.TemplateResponse("index.html", {"request": request, "years": years})
