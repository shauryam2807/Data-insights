window.renderCharts = function(numStats, catStats) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';

    // Color palette - professional, muted tones
    const colors = [
        'rgba(99, 102, 241, 0.85)',   // indigo
        'rgba(34, 197, 94, 0.85)',    // green
        'rgba(234, 179, 8, 0.85)',    // amber
        'rgba(239, 68, 68, 0.85)',    // red
        'rgba(168, 85, 247, 0.85)',   // purple
        'rgba(14, 165, 233, 0.85)',   // sky
        'rgba(249, 115, 22, 0.85)',   // orange
        'rgba(236, 72, 153, 0.85)',   // pink
    ];

    const borderColors = colors.map(c => c.replace('0.85', '1'));

    // Chart.js global defaults for dark theme
    Chart.defaults.color = '#9ca3af';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;

    function createCanvas(id, title) {
        const wrapper = document.createElement('div');
        wrapper.className = 'chart-wrapper';
        wrapper.innerHTML = `
            <p style="font-size:0.75em; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; color:#6b7280; margin-bottom:10px;">${title}</p>
            <canvas id="${id}"></canvas>
        `;
        container.appendChild(wrapper);
        return document.getElementById(id);
    }

    // ===== CHART 1: Horizontal Bar - Numeric Averages (Top 6) =====
    if (numStats && Object.keys(numStats).length > 0) {
        const entries = Object.entries(numStats)
            .sort((a, b) => Math.abs(b[1].mean) - Math.abs(a[1].mean))
            .slice(0, 6);

        const labels = entries.map(([col]) => col);
        const means = entries.map(([, s]) => s.mean);

        new Chart(createCanvas('num-chart', 'Average Values by Feature'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average',
                    data: means,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: borderColors.slice(0, labels.length),
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.65,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1a1d2e',
                        titleColor: '#e8eaf0',
                        bodyColor: '#9ca3af',
                        borderColor: '#2a2d3e',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => ` Average: ${ctx.raw.toLocaleString()}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: { color: '#6b7280', font: { size: 11 } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#e8eaf0', font: { size: 11, weight: 500 } }
                    }
                }
            }
        });
    }

    // ===== CHART 2: Doughnut - Top Category =====
    if (catStats && Object.keys(catStats).length > 0) {
        const col = Object.keys(catStats)[0];
        const topValues = catStats[col].top_values;
        const labels = Object.keys(topValues);
        const values = Object.values(topValues);

        new Chart(createCanvas('cat-chart', `${col} Breakdown`), {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: '#1a1d2e',
                    borderWidth: 3,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '55%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#9ca3af',
                            padding: 12,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1d2e',
                        titleColor: '#e8eaf0',
                        bodyColor: '#9ca3af',
                        borderColor: '#2a2d3e',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 10,
                        callbacks: {
                            label: (ctx) => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((ctx.raw / total) * 100).toFixed(1);
                                return ` ${ctx.label}: ${ctx.raw.toLocaleString()} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // ===== CHART 3: Min/Max Range Chart (if 3+ numeric cols) =====
    if (numStats && Object.keys(numStats).length >= 3) {
        const entries = Object.entries(numStats).slice(0, 6);
        const labels = entries.map(([col]) => col);
        const mins = entries.map(([, s]) => s.min);
        const maxs = entries.map(([, s]) => s.max);
        const medians = entries.map(([, s]) => s.median);

        new Chart(createCanvas('range-chart', 'Value Ranges (Min / Median / Max)'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Min',
                        data: mins,
                        backgroundColor: 'rgba(34, 197, 94, 0.7)',
                        borderRadius: 4,
                        barPercentage: 0.7,
                    },
                    {
                        label: 'Median',
                        data: medians,
                        backgroundColor: 'rgba(99, 102, 241, 0.7)',
                        borderRadius: 4,
                        barPercentage: 0.7,
                    },
                    {
                        label: 'Max',
                        data: maxs,
                        backgroundColor: 'rgba(239, 68, 68, 0.7)',
                        borderRadius: 4,
                        barPercentage: 0.7,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#9ca3af',
                            usePointStyle: true,
                            pointStyle: 'circle',
                            padding: 15,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1d2e',
                        titleColor: '#e8eaf0',
                        bodyColor: '#9ca3af',
                        borderColor: '#2a2d3e',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 10,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#9ca3af', font: { size: 10 }, maxRotation: 30 }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: { color: '#6b7280', font: { size: 10 } }
                    }
                }
            }
        });
    }

    // ===== CHART 4: Second categorical column (if exists) =====
    if (catStats && Object.keys(catStats).length > 1) {
        const col = Object.keys(catStats)[1];
        const topValues = catStats[col].top_values;
        const labels = Object.keys(topValues);
        const values = Object.values(topValues);

        new Chart(createCanvas('cat2-chart', `${col} Breakdown`), {
            type: 'polarArea',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.slice(0, labels.length).map(c => c.replace('0.85', '0.6')),
                    borderColor: '#1a1d2e',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#9ca3af',
                            padding: 10,
                            usePointStyle: true,
                            pointStyle: 'circle',
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1d2e',
                        titleColor: '#e8eaf0',
                        bodyColor: '#9ca3af',
                        borderColor: '#2a2d3e',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 10,
                    }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { display: false }
                    }
                }
            }
        });
    }
}
