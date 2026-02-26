"""Playwright end-to-end tests for the Pitwall lap comparison feature.

Test fixture: 2024 Round 1 (Bahrain), VER vs HAM.
"""

import multiprocessing
import time

import pytest
import uvicorn
from playwright.sync_api import Page, expect

SERVER_PORT = 8765
SERVER_URL = f"http://localhost:{SERVER_PORT}"


def _run_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=SERVER_PORT, log_level="error")


@pytest.fixture(scope="module", autouse=True)
def server():
    proc = multiprocessing.Process(target=_run_server, daemon=True)
    proc.start()
    # Wait for server to be ready
    import httpx
    for _ in range(30):
        try:
            r = httpx.get(f"{SERVER_URL}/")
            if r.status_code == 200:
                break
        except httpx.ConnectError:
            time.sleep(0.2)
    yield
    proc.terminate()
    proc.join(timeout=5)


def test_page_loads_with_dropdowns(page: Page):
    page.goto(SERVER_URL)
    expect(page.locator("#year-select")).to_be_visible()
    expect(page.locator("#event-select")).to_be_visible()
    # Driver selects should be disabled initially
    expect(page.locator("#driver1-select")).to_be_disabled()


def test_year_populates_races(page: Page):
    page.goto(SERVER_URL)
    page.select_option("#year-select", "2024")
    # Wait for HTMX to populate events
    page.wait_for_function(
        "document.querySelector('#event-select').options.length > 1"
    )
    options = page.locator("#event-select option")
    # Should have "Select race" + actual races
    assert options.count() > 1
    # Check Bahrain is in there
    assert "Bahrain" in page.locator("#event-select").inner_html()


def test_race_populates_drivers(page: Page):
    page.goto(SERVER_URL)
    page.select_option("#year-select", "2024")
    page.wait_for_function(
        "document.querySelector('#event-select').options.length > 1"
    )
    page.select_option("#event-select", "1")  # Round 1
    # Wait for driver selects to be populated
    page.wait_for_function(
        "document.querySelector('#driver1-select') && "
        "document.querySelector('#driver1-select').options.length > 1"
    )
    d1_html = page.locator("#driver1-select").inner_html()
    assert "Verstappen" in d1_html
    assert "Hamilton" in d1_html


def test_comparison_renders_chart(page: Page):
    page.goto(SERVER_URL)
    page.select_option("#year-select", "2024")
    page.wait_for_function(
        "document.querySelector('#event-select').options.length > 1"
    )
    page.select_option("#event-select", "1")
    page.wait_for_function(
        "document.querySelector('#driver1-select') && "
        "document.querySelector('#driver1-select').options.length > 1"
    )
    page.select_option("#driver1-select", "VER")
    page.select_option("#driver2-select", "HAM")

    # Wait for chart to render (canvas becomes visible)
    page.wait_for_selector("#lap-chart:not(.hidden)", timeout=10000)
    canvas = page.locator("#lap-chart")
    expect(canvas).to_be_visible()


def test_stats_panel_displays(page: Page):
    page.goto(SERVER_URL)
    page.select_option("#year-select", "2024")
    page.wait_for_function(
        "document.querySelector('#event-select').options.length > 1"
    )
    page.select_option("#event-select", "1")
    page.wait_for_function(
        "document.querySelector('#driver1-select') && "
        "document.querySelector('#driver1-select').options.length > 1"
    )
    page.select_option("#driver1-select", "VER")
    page.select_option("#driver2-select", "HAM")

    # Wait for stats to appear
    page.wait_for_selector("#stats-container:not(.hidden)", timeout=10000)
    stats = page.locator("#stats-container")
    expect(stats).to_be_visible()
    stats_text = stats.inner_text()
    assert "Verstappen" in stats_text
    assert "Hamilton" in stats_text
    assert "Fastest" in stats_text
    assert "Avg pace" in stats_text


def test_changing_driver_updates_chart(page: Page):
    page.goto(SERVER_URL)
    page.select_option("#year-select", "2024")
    page.wait_for_function(
        "document.querySelector('#event-select').options.length > 1"
    )
    page.select_option("#event-select", "1")
    page.wait_for_function(
        "document.querySelector('#driver1-select') && "
        "document.querySelector('#driver1-select').options.length > 1"
    )
    page.select_option("#driver1-select", "VER")
    page.select_option("#driver2-select", "HAM")
    page.wait_for_selector("#stats-container:not(.hidden)", timeout=10000)

    # Change driver 2 to NOR
    page.select_option("#driver2-select", "NOR")
    # Stats should update to show Norris
    page.wait_for_function(
        "document.querySelector('#stats-container').innerText.includes('Norris')",
        timeout=10000,
    )
    assert "Norris" in page.locator("#stats-container").inner_text()
