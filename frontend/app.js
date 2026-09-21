document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadSection = document.getElementById('upload-section');
    const dashboard = document.getElementById('dashboard');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-msg');

    browseBtn.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFileUpload(e.target.files[0]);
    });

    async function handleFileUpload(file) {
        errorMsg.classList.add('hidden');
        dropZone.classList.add('hidden');
        loading.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/analyze', { method: 'POST', body: formData });
            const data = await response.json();

            if (data.status === 'success') {
                renderDashboard(data);
                uploadSection.classList.add('hidden');
                dashboard.classList.remove('hidden');
            } else {
                throw new Error(data.message || 'Analysis failed');
            }
        } catch (error) {
            errorMsg.textContent = 'Error: ' + error.message;
            errorMsg.classList.remove('hidden');
            dropZone.classList.remove('hidden');
            loading.classList.add('hidden');
        }
    }

    function renderDashboard(data) {
        // 1. Render Key Metrics Row (Horizontal)
        const metricsRow = document.getElementById('metrics-row');
        const healthScore = data.health_report.score;
        const totalIssues = data.health_report.duplicates_found + 
            Object.values(data.health_report.missing_values_fixed).reduce((a, b) => a + b, 0);

        metricsRow.innerHTML = `
            <div class="metric-card health">
                <div class="metric-icon"><i class="fas fa-heartbeat"></i></div>
                <span class="metric-value">${healthScore}</span>
                <span class="metric-label">Health Score</span>
            </div>
            <div class="metric-card rows">
                <div class="metric-icon"><i class="fas fa-layer-group"></i></div>
                <span class="metric-value">${data.rows.toLocaleString()}</span>
                <span class="metric-label">Rows Analyzed</span>
            </div>
            <div class="metric-card cols">
                <div class="metric-icon"><i class="fas fa-columns"></i></div>
                <span class="metric-value">${data.columns}</span>
                <span class="metric-label">Features</span>
            </div>
            <div class="metric-card issues">
                <div class="metric-icon"><i class="fas fa-wrench"></i></div>
                <span class="metric-value">${totalIssues}</span>
                <span class="metric-label">Issues Fixed</span>
            </div>
        `;

        // 2. Health Score Circle
        const scoreEl = document.getElementById('health-score');
        scoreEl.textContent = healthScore;
        const circle = scoreEl.parentElement;
        if (healthScore >= 90) circle.style.borderColor = 'var(--success)';
        else if (healthScore >= 70) circle.style.borderColor = 'var(--warning)';
        else circle.style.borderColor = 'var(--danger)';

        // 3. Health Issues List
        const issuesList = document.getElementById('health-issues');
        issuesList.innerHTML = '';
        if (data.health_report.duplicates_found > 0) {
            issuesList.innerHTML += `<li><i class="fas fa-check-circle" style="color:var(--success); margin-right:5px;"></i> Removed ${data.health_report.duplicates_found} duplicate rows</li>`;
        }
        if (data.health_report.null_rows_removed > 0) {
            issuesList.innerHTML += `<li><i class="fas fa-check-circle" style="color:var(--success); margin-right:5px;"></i> Removed ${data.health_report.null_rows_removed} rows with null values</li>`;
            issuesList.innerHTML += `<li><i class="fas fa-compress-alt" style="color:var(--primary); margin-right:5px;"></i> ${data.health_report.rows_before} &rarr; ${data.health_report.rows_after} rows</li>`;
        }
        for (const [col, count] of Object.entries(data.health_report.missing_values_fixed)) {
            issuesList.innerHTML += `<li><i class="fas fa-exclamation-triangle" style="color:var(--warning); margin-right:5px;"></i> Column <strong>${col}</strong> had ${count} nulls</li>`;
        }
        if (Object.keys(data.health_report.outliers_flagged || {}).length > 0) {
            for (const [col, count] of Object.entries(data.health_report.outliers_flagged)) {
                issuesList.innerHTML += `<li><i class="fas fa-exclamation-triangle" style="color:var(--warning); margin-right:5px;"></i> ${count} outliers flagged in <strong>${col}</strong></li>`;
            }
        }
        if (issuesList.innerHTML === '') {
            issuesList.innerHTML = '<li style="color:var(--success)"><i class="fas fa-star" style="margin-right:5px;"></i> Data was perfectly clean!</li>';
        }

        // 4. Charts & Insights
        if (window.renderCharts) window.renderCharts(data.basic_stats, data.categorical_stats);
        if (window.renderInsights) window.renderInsights(data.insights, data.anomalies);
    }
});
