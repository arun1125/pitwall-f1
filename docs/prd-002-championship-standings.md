# PRD-002: Championship Standings Race Chart

## Problem Statement

There's no way to visualize how the championship battle evolved across a season. The database has pre-computed cumulative points per round for every driver (2018-2025), but without a chart you can't see momentum shifts, title fight crossovers, or when a driver pulled away.

## Solution

A dedicated Championship page (accessible via a new nav bar) with a line chart showing cumulative points across all rounds of a season. Every driver is plotted in their team color — the top 5 in the standings are bold, the rest faded to 30% opacity. A clickable Chart.js legend lets users toggle individual drivers on/off. A Driver/Constructor toggle switches between individual and team-aggregated standings. Hovering a point shows the race name and points scored that round.

## User Stories

1. As a user, I want a navigation bar with tabs for "Lap Comparison" and "Championship", so that I can switch between features.
2. As a user, I want the nav bar to highlight the active page, so that I know which view I'm on.
3. As a user, I want to select a year from a dropdown on the Championship page, so that I can view any season from 2018-2025.
4. As a user, I want to see a line chart with X = round number and Y = cumulative points, so that I can see the championship race unfold.
5. As a user, I want every driver plotted as a line in their team color, so that the chart feels authentic to F1.
6. As a user, I want the top 5 drivers (by final standings) displayed with bold lines, so that the title fight is visually prominent.
7. As a user, I want drivers outside the top 5 shown at 30-40% opacity, so that they're visible but don't compete for attention.
8. As a user, I want to hover over a data point and see the race name and points scored that round (e.g. "R5 — Monaco GP: +25pts (Total: 110pts)"), so that I can understand specific rounds.
9. As a user, I want to click a driver's name in the legend to toggle their line on/off, so that I can focus on specific battles.
10. As a user, I want a Driver/Constructor toggle button, so that I can switch between individual and team championship views.
11. As a user, I want the constructor view to aggregate both drivers' points per team and plot one line per team in the team color, so that I can see the constructors' championship.
12. As a user, I want the chart to auto-load for the most recent season when I first visit the page, so that I see useful data immediately.
13. As a user, I want the page to work on mobile, so that I can check standings on my phone.
14. As a user, I want the page to use the Pitwall theme (light background, F1 red accent, Inter font), so that it matches the rest of the app.

## Implementation Decisions

### Modules

1. **Navigation** — Add a tab/nav bar to `base.html` that appears on all pages. Two tabs: "Lap Comparison" (links to `/`) and "Championship" (links to `/championship`). Active tab highlighted with F1 red underline. This is the first multi-page change to the app.

2. **Championship API** — Two endpoints:
   - `GET /api/championship/drivers?year=YYYY` — Returns per-driver data: `{ drivers: [{ code, name, team, team_color, final_position, rounds: [{ round, race_name, round_points, cumulative_points }] }] }`. Joins `championship_progression` with `events` for race names. Sorted by final position (last round's `position` field).
   - `GET /api/championship/constructors?year=YYYY` — Aggregates points by team: `{ constructors: [{ team, team_color, rounds: [{ round, race_name, round_points, cumulative_points }] }] }`. Computed by summing both drivers' `round_points` and `cumulative_points` per team per round.

3. **Championship Page** — New route `GET /championship` rendering `championship.html`:
   - Year dropdown (pre-loaded, default to most recent year)
   - Driver/Constructor toggle button
   - Chart.js line chart with all drivers/teams
   - Top 5 lines at full opacity, rest at 30%
   - Clickable legend (Chart.js built-in behavior)
   - Tooltips with race name + points scored
   - Responsive layout matching existing pages

4. **Tests** — pytest for both API endpoints + Playwright for the championship page.

### Architecture

- Team color from `championship_progression` already includes `#` prefix — no conversion needed (unlike `driver_info`).
- Race names come from joining `championship_progression.round` with `events.round` on same year.
- Constructor aggregation is computed in SQL: `GROUP BY team, round`.
- The "top 5" determination uses `position` from the final round of the season.
- Chart.js `legend.onClick` is built-in — clicking a legend item toggles the dataset. No custom code needed.
- Opacity control via `borderColor` alpha channel: full opacity for top 5, `rgba(..., 0.3)` for others.

## Testing Decisions

### What Makes a Good Test

Tests verify external behavior through the API contract and browser interactions. No testing of internal SQL construction.

### Modules Under Test

1. **Championship API (pytest + TestClient)**
   - `/api/championship/drivers?year=2024` returns all drivers with correct cumulative points
   - Final position matches expected standings (VER should be position 1 in 2024)
   - Round data includes race names from events table
   - `/api/championship/constructors?year=2024` returns aggregated team data
   - Constructor points = sum of both drivers' points per round
   - Invalid year returns empty results
   - Missing year param returns 422

2. **Championship Page (Playwright)**
   - Page loads at `/championship`
   - Year dropdown is present with valid years
   - Chart renders with canvas element visible
   - Changing year updates the chart
   - Constructor toggle switches the chart view
   - Nav bar links work between pages

## Out of Scope

- Sprint race points breakdown
- Points-per-race bar chart overlay
- Teammate comparison mode
- Historical multi-season comparison
- Animation of the chart building up round by round
- Constructors' championship as a separate page (it's a toggle on this page)

## Further Notes

- The `championship_progression` table already has `team_color` with `#` prefix — different from `driver_info` which doesn't. The API should pass colors through as-is.
- 2024 had 24 rounds and 24 unique drivers (due to mid-season driver changes). The chart should handle this gracefully — drivers who joined mid-season will have data starting from their first race.
- Chart.js handles 20+ datasets well but the legend gets long. On mobile, consider placing the legend below the chart rather than to the side.
