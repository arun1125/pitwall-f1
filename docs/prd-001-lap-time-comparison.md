# PRD-001: Lap Time Comparison Chart

## Problem Statement

There's no way to visually compare how two drivers performed across a race lap-by-lap. Raw timing data exists in the database (242K lap records, 2018-2025), but without a chart overlay, spotting pace differences, strategy divergence, and key moments requires manual analysis.

## Solution

A single-page web app with cascading dropdowns (Year → Race → Driver 1 + Driver 2) that renders an overlaid line chart of both drivers' lap times. The chart color-codes tire compounds, visually distinguishes pit/inaccurate laps, and uses team colors for driver identification. A summary stats panel below the chart shows fastest lap, average pace, and gap at finish.

This is the first feature built in the app, so it includes full application scaffolding (FastAPI, HTMX, Tailwind, Chart.js).

## User Stories

1. As a user, I want to select a year from a dropdown, so that I can narrow down to a specific season.
2. As a user, I want to see a list of races for the selected year, so that I can pick the event I'm interested in.
3. As a user, I want the race dropdown to update automatically when I change the year, so that I always see valid options.
4. As a user, I want to select two drivers from dropdowns filtered to participants of the chosen race, so that I only see valid driver options.
5. As a user, I want the driver dropdowns to update when I change the race, so that the driver list matches the selected event.
6. As a user, I want to see both drivers' lap times overlaid on a single line chart (X = lap number, Y = lap time in seconds), so that I can visually compare their pace.
7. As a user, I want each driver's line colored with their team color from the database, so that the chart feels authentic to F1.
8. As a user, I want same-team driver comparisons to use a lightened/darkened variant for the second driver, so that the two lines remain distinguishable.
9. As a user, I want line segments colored by tire compound (red = Soft, yellow = Medium, white = Hard, green = Intermediate, blue = Wet), so that I can see strategy at a glance.
10. As a user, I want pit laps and inaccurate laps to appear as dashed or greyed-out markers rather than being hidden, so that I can see where stops happened without distorting the Y-axis scale.
11. As a user, I want the Y-axis to auto-scale to the data range (excluding extreme outliers like pit laps), so that the chart is always readable.
12. As a user, I want to see summary stats below the chart — fastest lap, average pace (excluding pit laps), and gap at finish — for each driver, so that I get key numbers without eyeballing the chart.
13. As a user, I want the page to work on mobile, so that I can check comparisons on my phone.
14. As a user, I want the page to use the F1 light theme (#FAFAFA background, #E10600 accent, Inter font), so that it matches the Pitwall brand.
15. As a user, I want the chart to load via HTMX without a full page refresh, so that switching between comparisons feels fast.

## Implementation Decisions

### Modules

1. **App Scaffolding** — FastAPI application factory, static file serving, Jinja2 templating, base HTML template pulling in HTMX, Tailwind (CDN), Chart.js (CDN), and Inter font. Single entry point (`main.py`) with a router-based structure.

2. **Sessions API** — Three endpoints that power the cascading dropdowns:
   - `GET /api/years` → list of available years
   - `GET /api/events?year=YYYY` → races for that year (round, name, country, date)
   - `GET /api/drivers?year=YYYY&round=N` → drivers who participated in that race (driver_code, full_name, team, team_color)

3. **Lap Comparison API** — Single endpoint that returns everything the chart needs:
   - `GET /api/laps/compare?year=YYYY&round=N&d1=VER&d2=HAM`
   - Response: `{ driver1: { code, name, team, team_color, laps: [{lap, time_sec, compound, is_pit, is_accurate}], stats: {fastest_lap, avg_pace, finish_position} }, driver2: { ... } }`
   - Lap times converted from ms to seconds in the API
   - `is_pit` derived from `is_pit_in` or `is_pit_out` flags
   - Stats computed server-side: fastest lap (min of accurate laps), average pace (mean of accurate non-pit laps), finishing position from results table

4. **Frontend Page** — Single page (`/`) with:
   - Cascading dropdowns wired with HTMX (`hx-get`, `hx-trigger="change"`)
   - Chart.js line chart rendered via a small JS module
   - Compound colors applied per-segment on the line
   - Pit laps rendered as dashed/hollow points
   - Same-team detection: if both team_colors match, lighten driver 2's color by ~30%
   - Stats panel: simple grid/table below the chart

### Architecture

- Database access via a shared `get_db()` dependency that opens a read-only SQLite connection.
- All SQL queries filter `session_type = 'R'` (race only) for this feature.
- Lap data filtered to `is_accurate = 1` for stats calculations, but all laps returned for chart rendering (with flags).
- No ORM — raw SQL with parameterized queries.

### Same-Team Color Handling

When both drivers share the same `team_color`, the API response includes both the original color and a `color_variant` field. The frontend lightens driver 2's hex by adjusting HSL lightness +20%.

## Testing Decisions

### What Makes a Good Test

Tests verify external behavior through the API contract — given specific query parameters, assert the response shape, status codes, and data correctness. Do not test internal SQL query construction or helper function internals unless they have independent value.

### Modules Under Test

1. **Sessions API (pytest + TestClient)**
   - Returns correct years from the database
   - Returns events filtered by year
   - Returns only drivers who participated in a specific race
   - Returns 400/422 for invalid parameters

2. **Lap Comparison API (pytest + TestClient)**
   - Returns correct lap data for two valid drivers in a known race
   - Lap times are in seconds (not milliseconds)
   - Stats are computed correctly (fastest lap, average pace)
   - Pit laps are flagged correctly
   - Handles edge cases: driver who DNF'd early, driver not in the race (404)

3. **Data layer (pytest)**
   - Database connection helper works
   - Query functions return expected shapes
   - Parameterized queries prevent injection

4. **Frontend (Playwright)**
   - Page loads and renders the dropdowns
   - Selecting a year populates the race dropdown
   - Selecting a race populates both driver dropdowns
   - Selecting two drivers and triggering comparison renders a chart (canvas element exists and has content)
   - Stats panel displays values for both drivers

### Test Infrastructure

- `pytest` with `httpx.AsyncClient` or `TestClient` for API tests
- `playwright` (Python) for browser tests
- Test database: use the real `f1data.db` (read-only, deterministic data)
- Known test fixtures: 2024 Round 1 (Bahrain) with VER and HAM as test drivers

## Out of Scope

- Qualifying lap comparison (race only for V1)
- More than 2 drivers on the same chart
- Sector time breakdown (just total lap time)
- Safety car period overlay (laps are shown but no SC markers)
- Telemetry or speed trace overlays
- Data export (CSV, image)
- URL sharing / deep linking to a specific comparison
- Sprint race support

## Further Notes

- The database is read-only and pre-built. No migrations or writes needed.
- Lap times in the DB are milliseconds — the API must convert to seconds for the frontend.
- Team colors in the DB are hex without `#` prefix (e.g. `3671C6`). The API should prepend `#`.
- The `is_accurate` flag exists on laps — use it to distinguish clean laps from outliers.
- This PRD covers the first feature and includes scaffolding. Subsequent features can assume the app structure exists.
