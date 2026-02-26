let lapChart = null;

function tryLoadComparison() {
    const year = document.getElementById('year-select')?.value;
    const round = document.getElementById('event-select')?.value;
    const d1 = document.getElementById('driver1-select')?.value;
    const d2 = document.getElementById('driver2-select')?.value;

    if (!year || !round || !d1 || !d2 || d1 === d2) return;

    const url = `/api/laps/compare?year=${year}&round=${round}&d1=${d1}&d2=${d2}`;
    fetch(url)
        .then(r => r.json())
        .then(data => renderChart(data))
        .catch(err => console.error('Failed to load comparison:', err));
}

// Compound colors
const COMPOUND_COLORS = {
    SOFT: '#E53E3E',
    MEDIUM: '#D69E2E',
    HARD: '#E2E8F0',
    INTERMEDIATE: '#38A169',
    WET: '#3182CE',
};

function lightenColor(hex, amount) {
    hex = hex.replace('#', '');
    const r = Math.min(255, parseInt(hex.slice(0, 2), 16) + amount);
    const g = Math.min(255, parseInt(hex.slice(2, 4), 16) + amount);
    const b = Math.min(255, parseInt(hex.slice(4, 6), 16) + amount);
    return `rgb(${r}, ${g}, ${b})`;
}

function buildSegmentColors(laps, baseColor) {
    return laps.map(lap => {
        if (lap.is_pit || !lap.is_accurate) return '#D1D5DB';
        return COMPOUND_COLORS[lap.compound] || baseColor;
    });
}

function buildPointStyles(laps) {
    return laps.map(lap => {
        if (lap.is_pit || !lap.is_accurate) return 'crossRot';
        return 'circle';
    });
}

function buildPointRadii(laps) {
    return laps.map(lap => {
        if (lap.is_pit || !lap.is_accurate) return 4;
        return 2;
    });
}

function formatLapTime(seconds) {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);
    return mins > 0 ? `${mins}:${secs.padStart(6, '0')}` : `${secs}s`;
}

function renderChart(data) {
    const d1 = data.driver1;
    const d2 = data.driver2;

    // Determine colors — lighten d2 if same team
    let color1 = d1.team_color;
    let color2 = d2.team_color;
    if (color1 === color2) {
        color2 = lightenColor(color2, 60);
    }

    // Filter data for Y-axis scaling (exclude pit/inaccurate laps)
    const cleanTimes = [
        ...d1.laps.filter(l => l.is_accurate && !l.is_pit && l.time_sec).map(l => l.time_sec),
        ...d2.laps.filter(l => l.is_accurate && !l.is_pit && l.time_sec).map(l => l.time_sec),
    ];
    const minTime = Math.floor(Math.min(...cleanTimes) - 1);
    const maxTime = Math.ceil(Math.max(...cleanTimes) + 2);

    const canvas = document.getElementById('lap-chart');
    const placeholder = document.getElementById('chart-placeholder');
    placeholder.classList.add('hidden');
    canvas.classList.remove('hidden');

    if (lapChart) lapChart.destroy();

    lapChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: d1.laps.map(l => l.lap),
            datasets: [
                {
                    label: `${d1.name} (${d1.team})`,
                    data: d1.laps.map(l => l.time_sec),
                    borderColor: color1,
                    backgroundColor: color1,
                    segment: {
                        borderColor: ctx => {
                            const colors = buildSegmentColors(d1.laps, color1);
                            return colors[ctx.p0DataIndex] || color1;
                        },
                        borderDash: ctx => {
                            const lap = d1.laps[ctx.p0DataIndex];
                            return (lap && (lap.is_pit || !lap.is_accurate)) ? [5, 5] : [];
                        },
                    },
                    pointBackgroundColor: ctx => {
                        const colors = buildSegmentColors(d1.laps, color1);
                        return colors[ctx.dataIndex] || color1;
                    },
                    pointStyle: buildPointStyles(d1.laps),
                    pointRadius: buildPointRadii(d1.laps),
                    borderWidth: 2,
                    tension: 0.1,
                    spanGaps: true,
                },
                {
                    label: `${d2.name} (${d2.team})`,
                    data: d2.laps.map(l => l.time_sec),
                    borderColor: color2,
                    backgroundColor: color2,
                    segment: {
                        borderColor: ctx => {
                            const colors = buildSegmentColors(d2.laps, color2);
                            return colors[ctx.p0DataIndex] || color2;
                        },
                        borderDash: ctx => {
                            const lap = d2.laps[ctx.p0DataIndex];
                            return (lap && (lap.is_pit || !lap.is_accurate)) ? [5, 5] : [];
                        },
                    },
                    pointBackgroundColor: ctx => {
                        const colors = buildSegmentColors(d2.laps, color2);
                        return colors[ctx.dataIndex] || color2;
                    },
                    pointStyle: buildPointStyles(d2.laps),
                    pointRadius: buildPointRadii(d2.laps),
                    borderWidth: 2,
                    tension: 0.1,
                    spanGaps: true,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const driver = ctx.datasetIndex === 0 ? d1 : d2;
                            const lap = driver.laps[ctx.dataIndex];
                            let label = `${driver.code}: ${formatLapTime(ctx.parsed.y)}`;
                            if (lap) label += ` (${lap.compound}${lap.is_pit ? ', PIT' : ''})`;
                            return label;
                        },
                    },
                },
            },
            scales: {
                x: {
                    title: { display: true, text: 'Lap' },
                },
                y: {
                    title: { display: true, text: 'Lap Time (s)' },
                    min: minTime,
                    max: maxTime,
                },
            },
        },
    });

    // Render stats
    renderStats(d1, d2, color1, color2);
}

function renderStats(d1, d2, color1, color2) {
    const container = document.getElementById('stats-container');
    container.classList.remove('hidden');
    container.innerHTML = `
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Summary</h3>
        <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
                <div class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full inline-block" style="background:${color1}"></span>
                    <span class="font-medium text-sm">${d1.name}</span>
                </div>
                <div class="text-xs text-gray-500 space-y-1 pl-5">
                    <div>Fastest: <span class="font-mono text-gray-900">${formatLapTime(d1.stats.fastest_lap)}</span></div>
                    <div>Avg pace: <span class="font-mono text-gray-900">${formatLapTime(d1.stats.avg_pace)}</span></div>
                    <div>Finished: <span class="font-mono text-gray-900">P${d1.stats.finish_position || '-'}</span></div>
                </div>
            </div>
            <div class="space-y-2">
                <div class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full inline-block" style="background:${color2}"></span>
                    <span class="font-medium text-sm">${d2.name}</span>
                </div>
                <div class="text-xs text-gray-500 space-y-1 pl-5">
                    <div>Fastest: <span class="font-mono text-gray-900">${formatLapTime(d2.stats.fastest_lap)}</span></div>
                    <div>Avg pace: <span class="font-mono text-gray-900">${formatLapTime(d2.stats.avg_pace)}</span></div>
                    <div>Finished: <span class="font-mono text-gray-900">P${d2.stats.finish_position || '-'}</span></div>
                </div>
            </div>
        </div>
    `;
}

// Listen for changes on driver selects (use event delegation since HTMX replaces them)
document.addEventListener('change', e => {
    if (e.target.id === 'driver1-select' || e.target.id === 'driver2-select') {
        tryLoadComparison();
    }
});
