let champChart = null;
let currentMode = 'drivers';

function hexToRgba(hex, alpha) {
    hex = hex.replace('#', '');
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function loadChampionship() {
    const year = document.getElementById('champ-year-select').value;
    if (!year) return;

    fetch(`/api/championship/drivers?year=${year}`)
        .then(r => r.json())
        .then(data => renderChampChart(data.drivers))
        .catch(err => console.error('Failed to load championship:', err));
}

function renderChampChart(drivers) {
    if (!drivers || drivers.length === 0) return;

    const canvas = document.getElementById('champ-chart');

    // Build round labels from first driver's data
    const roundLabels = drivers[0].rounds.map(r => `R${r.round}`);

    const datasets = drivers.map(driver => {
        const isTop5 = driver.final_position <= 5;
        const alpha = isTop5 ? 1 : 0.3;
        const color = driver.team_color;

        return {
            label: `${driver.code} — ${driver.name}`,
            data: driver.rounds.map(r => r.cumulative_points),
            borderColor: hexToRgba(color, alpha),
            backgroundColor: hexToRgba(color, alpha),
            borderWidth: isTop5 ? 2.5 : 1.5,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: color,
            tension: 0.2,
            // Store metadata for tooltips
            _rounds: driver.rounds,
            _code: driver.code,
        };
    });

    if (champChart) champChart.destroy();

    champChart = new Chart(canvas, {
        type: 'line',
        data: { labels: roundLabels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'line',
                        padding: 12,
                        font: { size: 11 },
                    },
                },
                tooltip: {
                    callbacks: {
                        title: ctx => {
                            const idx = ctx[0].dataIndex;
                            const ds = ctx[0].dataset;
                            const roundData = ds._rounds?.[idx];
                            if (roundData) return `R${roundData.round} — ${roundData.race_name}`;
                            return ctx[0].label;
                        },
                        label: ctx => {
                            const ds = ctx.dataset;
                            const roundData = ds._rounds?.[ctx.dataIndex];
                            if (roundData) {
                                return `${ds._code}: +${roundData.round_points}pts (Total: ${roundData.cumulative_points}pts)`;
                            }
                            return `${ds.label}: ${ctx.parsed.y}pts`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    title: { display: true, text: 'Round' },
                    grid: { display: false },
                },
                y: {
                    title: { display: true, text: 'Cumulative Points' },
                    beginAtZero: true,
                },
            },
        },
    });
}

// Year change
document.getElementById('champ-year-select').addEventListener('change', loadChampionship);

// Auto-load on page load (first/most recent year is already selected)
loadChampionship();
