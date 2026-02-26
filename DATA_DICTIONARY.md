# F1 Data Dictionary

Complete schema reference for `f1data.db`.

## Core Tables

### events
| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Season year |
| round | INTEGER | Round number in season |
| name | TEXT | Grand Prix name (e.g. "Bahrain Grand Prix") |
| country | TEXT | Country |
| circuit | TEXT | Circuit name |
| date | TEXT | Event date (ISO format) |
| format | TEXT | Event format |

### sessions
| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Season year |
| round | INTEGER | Round number |
| session_type | TEXT | "R" (race) or "Q" (qualifying) |
| session_name | TEXT | Full session name |
| date | TEXT | Session date |

### results
| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Season year |
| round | INTEGER | Round number |
| session_type | TEXT | "R" or "Q" |
| position | INTEGER | Finishing position |
| driver_code | TEXT | 3-letter code (e.g. "VER", "HAM") |
| driver_name | TEXT | Full name |
| team | TEXT | Team name |
| team_color | TEXT | Hex color without # |
| driver_number | INTEGER | Car number |
| grid_position | INTEGER | Starting grid position |
| status | TEXT | "Finished", "Retired", "+1 Lap", etc. |
| time | TEXT | Finishing time or gap |
| points | REAL | Points scored |
| positions_gained | INTEGER | Grid vs finish delta |

### laps
| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Season year |
| round | INTEGER | Round number |
| session_type | TEXT | "R" or "Q" |
| driver | TEXT | 3-letter driver code |
| lap_number | INTEGER | Lap number |
| lap_time_ms | REAL | Lap time in milliseconds |
| sector1_ms | REAL | Sector 1 time (ms) |
| sector2_ms | REAL | Sector 2 time (ms) |
| sector3_ms | REAL | Sector 3 time (ms) |
| compound | TEXT | SOFT, MEDIUM, HARD, INTERMEDIATE, WET |
| tire_life | INTEGER | Laps on current set |
| position | INTEGER | Position at end of lap |
| stint | INTEGER | Stint number (resets on pit stop) |
| is_pit_in | INTEGER | 1 if driver pitted this lap |
| is_pit_out | INTEGER | 1 if driver left pits this lap |
| is_accurate | INTEGER | 1 if timing data is reliable |

### driver_info
| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Season year |
| driver_code | TEXT | 3-letter code |
| driver_number | INTEGER | Car number |
| first_name | TEXT | First name |
| last_name | TEXT | Last name |
| full_name | TEXT | Full name |
| team | TEXT | Team name |
| team_color | TEXT | Hex color without # |
| headshot_url | TEXT | URL to driver headshot |

## Analytics Tables (Pre-computed)

### stint_analysis
Pre-computed tire degradation per driver per stint.
Key columns: year, round, driver, stint, compound, stint_laps, avg_lap_ms, deg_slope_ms, r_squared

### championship_progression
Cumulative points per driver per round.
Key columns: year, round, driver_code, cumulative_points, position

### driver_season_stats
Season aggregates for radar charts.
Key columns: year, driver_code, races, wins, podiums, poles, avg_finish, avg_grid, dnfs, points

## Supporting Tables

### pit_times
Pit stop timing. Key columns: year, round, session_type, driver, lap_number, pit_in_time_ms, pit_out_time_ms

### weather
Session weather data. Key columns: year, round, session_type, timestamp, air_temp, track_temp, humidity, pressure, rainfall, wind_speed, wind_direction

### qualifying_times
Best Q1/Q2/Q3 lap times. Key columns: year, round, driver_code, q1_ms, q2_ms, q3_ms

### intervals
Gap to leader per lap (1.38M rows). Key columns: year, round, driver, lap_number, gap_to_leader, interval

### race_control
Flag and safety car events. Key columns: year, round, session_type, timestamp, category, flag, message
