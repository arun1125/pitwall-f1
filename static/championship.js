let champChart = null;
let currentMode = 'drivers';

function hexToRgba(hex, alpha) {
    hex = hex.replace('#', '');
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function setActiveToggle(mode) {
    currentMode = mode;
    const btnDrivers = document.getElementById('btn-drivers');
    const btnConstructors = document.getElementById('btn-constructors');

    if (mode === 'drivers') {
        btnDrivers.classList.add('bg-f1red', 'text-white');
        btnDrivers.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-50');
        btnConstructors.classList.remove('bg-f1red', 'text-white');
        btnConstructors.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-50');
    } else {
        btnConstructors.classList.add('bg-f1red', 'text-white');
        btnConstructors.classList.remove('bg-white', 'text-gray-700', 'hover:bg-gray-50');
        btnDrivers.classList.remove('bg-f1red', 'text-white');
        btnDrivers.classList.add('bg-white', 'text-gray-700', 'hover:bg-gray-50');
    }
}

function loadChampionship() {
    const year = document.getElementById('champ-year-select').value;
    if (!year) return;

    const endpoint = currentMode === 'drivers'
        ? `/api/championship/drivers?year=${year}`
        : `/api/championship/constructors?year=${year}`;

    fetch(endpoint)
        .then(r => r.json())
        .then(data => {
            if (currentMode === 'drivers') {
                renderDriverChart(data.drivers);
            } else {
                renderConstructorChart(data.constructors);
            }
        })
        .catch(err => console.error('Failed to load championship:', err));
}

function renderDriverChart(drivers) {
    if (!drivers || drivers.length === 0) return;

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
            _rounds: driver.rounds,
            _code: driver.code,
        };
    });

    renderChart(roundLabels, datasets);
}

function renderConstructorChart(constructors) {
    if (!constructors || constructors.length === 0) return;

    const roundLabels = constructors[0].rounds.map(r => `R${r.round}`);

    const datasets = constructors.map(team => {
        const color = team.team_color;

        return {
            label: team.team,
            data: team.rounds.map(r => r.cumulative_points),
            borderColor: hexToRgba(color, 1),
            backgroundColor: hexToRgba(color, 1),
            borderWidth: 2.5,
            pointRadius: 0,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: color,
            tension: 0.2,
            _rounds: team.rounds,
            _code: team.team,
        };
    });

    renderChart(roundLabels, datasets);
}

function renderChart(labels, datasets) {
    const canvas = document.getElementById('champ-chart');

    if (champChart) champChart.destroy();

    champChart = new Chart(canvas, {
        type: 'line',
        data: { labels, datasets },
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

// Toggle buttons
document.getElementById('btn-drivers').addEventListener('click', () => {
    setActiveToggle('drivers');
    loadChampionship();
});

document.getElementById('btn-constructors').addEventListener('click', () => {
    setActiveToggle('constructors');
    loadChampionship();
});

// Year change
document.getElementById('champ-year-select').addEventListener('change', loadChampionship);

// Auto-load on page load (first/most recent year is already selected)
loadChampionship();
