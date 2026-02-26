# Pitwall — F1 Analytics App

Rebuild of an F1 analytics dashboard, built incrementally using agentic product development.

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** HTML + HTMX + Tailwind CSS (keep it simple, no React)
- **Database:** SQLite (pre-built, read-only — do NOT modify f1data.db)
- **Charts:** Chart.js or lightweight JS charting library

## Database

`f1data.db` is a pre-built SQLite database with 1.9M rows of F1 data (2018-2025).

### Key Tables

| Table | Rows | What it has |
|-------|------|-------------|
| `events` | 173 | Race calendar (year, round, name, country, circuit, date) |
| `sessions` | 346 | Race + Qualifying per event |
| `results` | 6,880 | Position, driver, team, grid, status, time, points |
| `laps` | 242,686 | Lap times (ms), sector times, compound, tire life, position, stint |
| `driver_info` | 103 | Driver names, numbers, teams, team colors, headshots |
| `stint_analysis` | 10,459 | Pre-computed tire degradation (regression slopes, R²) |
| `championship_progression` | 3,594 | Cumulative points per round |
| `driver_season_stats` | 173 | Season aggregates for radar charts |
| `pit_times` | 39,610 | Pit in/out times per lap |
| `weather` | 37,558 | Air/track temp, humidity, rainfall per session |
| `race_control` | 19,562 | Flags, safety car, DRS events |
| `intervals` | 1,382,233 | Gap-to-leader per lap |
| `qualifying_times` | 1,376 | Q1/Q2/Q3 best times |

### Common Queries

```sql
-- All events for a year
SELECT * FROM events WHERE year = 2024 ORDER BY round;

-- Race results
SELECT * FROM results WHERE year = 2024 AND round = 1 AND session_type = 'R' ORDER BY position;

-- Lap times for a driver in a race
SELECT * FROM laps WHERE year = 2024 AND round = 1 AND session_type = 'R' AND driver = 'VER' ORDER BY lap_number;

-- Driver info with team colors
SELECT * FROM driver_info WHERE year = 2024;
```

### Data Notes

- Lap times stored in milliseconds (divide by 1000 for seconds)
- Team colors are hex without # prefix (e.g. "3671C6" for Red Bull)
- `is_accurate` flag on laps — filter to `is_accurate = 1` for clean data
- Years: 2018-2025, Race + Qualifying only (no practice/sprint)

## Design

- Light theme: `#FAFAFA` background, `#FFFFFF` cards
- Accent: `#E10600` (F1 red)
- Font: Inter
- Mobile-friendly

## Rules

- Never write to the database. It's read-only reference data.
- Keep dependencies minimal. No complex build systems.
- Each feature should be a vertical slice (API endpoint + UI).
- Test with `pytest` for backend, manual QA for frontend.

## Workflow

This project uses an agentic development workflow:
1. `/write-a-prd` — Plan a feature through structured interview → PRD
2. `/prd-to-issues` — Break PRD into vertical-slice tasks
3. `./scripts/ralph-once.sh` — Execute one task per iteration
4. `./scripts/ralph-loop.sh N` — Execute N tasks autonomously
5. Manual QA after each ralph cycle

## Installed Skills

- `/write-a-prd` — Feature planning → PRD
- `/prd-to-issues` — PRD → implementation issues
- `/tdd` — Test-driven development loop
