window.renderInsights = function(insights, anomalies) {
    const container = document.getElementById('insights-container');
    container.innerHTML = '';

    // Map insight types to icons
    const iconMap = {
        'About': { icon: 'fa-database', cls: 'about' },
        'Data Cleaning': { icon: 'fa-broom', cls: 'cleaning' },
        'Summary': { icon: 'fa-chart-bar', cls: 'summary' },
        'Distribution': { icon: 'fa-chart-pie', cls: 'distribution' },
        'Concentration Risk': { icon: 'fa-exclamation-circle', cls: 'distribution' },
        'Data Quality': { icon: 'fa-info-circle', cls: 'summary' },
        'Risk Alert': { icon: 'fa-shield-alt', cls: 'risk' },
        'Relationship': { icon: 'fa-link', cls: 'relationship' },
        'Pattern': { icon: 'fa-project-diagram', cls: 'pattern' },
        'Segmentation': { icon: 'fa-object-group', cls: 'segmentation' },
        'Info': { icon: 'fa-info-circle', cls: 'about' }
    };

    if (!insights || insights.length === 0) {
        container.innerHTML = '<p style="color:var(--text-muted)">No significant insights found. Try a larger dataset.</p>';
    } else {
        insights.forEach((insight, i) => {
            const mapping = iconMap[insight.type] || { icon: 'fa-circle', cls: 'about' };
            
            // Determine border class
            let borderCls = '';
            if (insight.type === 'Risk Alert') borderCls = 'risk';
            else if (insight.type === 'Pattern' || insight.type === 'Relationship') borderCls = 'pattern';
            else if (insight.type === 'Summary' || insight.type === 'Data Quality') borderCls = 'summary';
            else if (insight.type === 'Distribution' || insight.type === 'Concentration Risk') borderCls = 'distribution';
            else if (insight.type === 'About') borderCls = 'about';
            else if (insight.type === 'Data Cleaning') borderCls = 'cleaning';

            container.innerHTML += `
                <div class="insight-item ${borderCls}" style="animation-delay: ${i * 0.04}s">
                    <div class="insight-header">
                        <div class="insight-type-icon ${mapping.cls}">
                            <i class="fas ${mapping.icon}"></i>
                        </div>
                        <span class="badge">${insight.badge}</span>
                    </div>
                    <p class="insight-text">${insight.text}</p>
                    <small class="insight-details">${insight.details}</small>
                </div>
            `;
        });
    }

    // Anomalies
    const anomalyContainer = document.getElementById('anomalies-container');
    anomalyContainer.innerHTML = '';
    
    if (!anomalies || anomalies.length === 0) {
        anomalyContainer.innerHTML = '<p style="color:var(--success)"><i class="fas fa-check-circle" style="margin-right:6px;"></i> No anomalies detected. All data points are within the expected range.</p>';
    } else {
        anomalyContainer.innerHTML += `<p style="color:var(--text-muted); margin-bottom:12px; font-size:0.85em;">${anomalies.length} record(s) flagged for manual review. These rows have values significantly outside normal ranges.</p>`;
        
        anomalies.forEach((anomaly, i) => {
            const reasons = anomaly.reasons.map(r => `<li>${r}</li>`).join('');
            let tags = '';
            for (let key in anomaly.data) {
                tags += `<span class="badge" style="margin:2px; background:rgba(255,255,255,0.04);">${key}: ${anomaly.data[key]}</span> `;
            }
            anomalyContainer.innerHTML += `
                <div class="anomaly-item" style="animation-delay: ${i * 0.06}s">
                    <strong style="color:var(--danger); font-size:0.9em;">Record #${anomaly.row_index}</strong>
                    <ul style="margin:6px 0 8px; padding-left:18px; color:var(--text-main); font-size:0.85em; line-height:1.7;">${reasons}</ul>
                    <div>${tags}</div>
                </div>
            `;
        });
    }
}
