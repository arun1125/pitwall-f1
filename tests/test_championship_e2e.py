"""Playwright end-to-end tests for the Championship standings feature.

Test fixture: 2024 season.
"""

import multiprocessing
import time

import pytest
import uvicorn
from playwright.sync_api import Page, expect

SERVER_PORT = 8766
SERVER_URL = f"http://localhost:{SERVER_PORT}"


def _run_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=SERVER_PORT, log_level="error")


@pytest.fixture(scope="module", autouse=True)
def server():
    proc = multiprocessing.Process(target=_run_server, daemon=True)
    proc.start()
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


def _wait_for_chart(page: Page):
    """Wait for Chart.js to render on the championship canvas."""
    page.wait_for_function(
        """() => {
            const canvas = document.getElementById('champ-chart');
            if (!canvas) return false;
            const chart = Chart.getChart(canvas);
            return chart && chart.data.datasets.length > 0;
        }""",
        timeout=10000,
    )


def test_championship_page_loads(page: Page):
    """Page loads with year dropdown and chart canvas."""
    page.goto(f"{SERVER_URL}/championship")
    expect(page.locator("#champ-year-select")).to_be_visible()
    expect(page.locator("#champ-chart")).to_be_visible()
    expect(page.locator("#btn-drivers")).to_be_visible()
    expect(page.locator("#btn-constructors")).to_be_visible()


def test_chart_renders_on_load(page: Page):
    """Chart auto-loads with driver data for the most recent season."""
    page.goto(f"{SERVER_URL}/championship")
    _wait_for_chart(page)
    # Verify Chart.js has datasets
    dataset_count = page.evaluate(
        "Chart.getChart(document.getElementById('champ-chart')).data.datasets.length"
    )
    assert dataset_count > 0


def test_changing_year_updates_chart(page: Page):
    """Selecting a different year reloads the chart with new data."""
    page.goto(f"{SERVER_URL}/championship")
    _wait_for_chart(page)

    # Get initial dataset labels
    initial_labels = page.evaluate(
        "Chart.getChart(document.getElementById('champ-chart')).data.datasets.map(d => d.label)"
    )

    # Switch to 2020
    page.select_option("#champ-year-select", "2020")

    # Wait for chart to update with different data
    page.wait_for_function(
        """() => {
            const chart = Chart.getChart(document.getElementById('champ-chart'));
            if (!chart || chart.data.datasets.length === 0) return false;
            const labels = chart.data.datasets.map(d => d.label);
            return labels.join(',') !== '%s';
        }"""
        % ",".join(initial_labels),
        timeout=10000,
    )

    new_labels = page.evaluate(
        "Chart.getChart(document.getElementById('champ-chart')).data.datasets.map(d => d.label)"
    )
    assert new_labels != initial_labels


def test_constructor_toggle_switches_view(page: Page):
    """Clicking Constructors button switches to constructor chart."""
    page.goto(f"{SERVER_URL}/championship")
    _wait_for_chart(page)

    # Get driver dataset count
    driver_count = page.evaluate(
        "Chart.getChart(document.getElementById('champ-chart')).data.datasets.length"
    )

    # Click Constructors toggle
    page.click("#btn-constructors")

    # Wait for chart to reload with fewer datasets (10 teams vs ~20 drivers)
    page.wait_for_function(
        """(driverCount) => {
            const chart = Chart.getChart(document.getElementById('champ-chart'));
            return chart && chart.data.datasets.length > 0 && chart.data.datasets.length !== driverCount;
        }""",
        arg=driver_count,
        timeout=10000,
    )

    constructor_count = page.evaluate(
        "Chart.getChart(document.getElementById('champ-chart')).data.datasets.length"
    )
    # Constructors should be ~10 teams, drivers ~20+
    assert constructor_count < driver_count


def test_nav_to_lap_comparison(page: Page):
    """Nav bar link navigates from Championship to Lap Comparison page."""
    page.goto(f"{SERVER_URL}/championship")
    page.click('a[href="/"]')
    page.wait_for_url(f"{SERVER_URL}/")
    expect(page.locator("#year-select")).to_be_visible()


def test_nav_to_championship(page: Page):
    """Nav bar link navigates from Lap Comparison to Championship page."""
    page.goto(SERVER_URL)
    page.click('a[href="/championship"]')
    page.wait_for_url(f"{SERVER_URL}/championship")
    expect(page.locator("#champ-year-select")).to_be_visible()
