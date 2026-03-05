document.addEventListener('DOMContentLoaded', () => {
    // --- State ---
    let scanData = null;
    let anomalyData = null;

    // --- Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const target = item.getAttribute('data-section');
            
            navItems.forEach(i => i.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            item.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (target === 'anomaly' && !anomalyData) loadAnomalyData();
            if (target === 'intel') renderIntelCharts();
        });
    });

    // --- Fetch Data ---
    async function loadDashboard() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();
            scanData = data;

            updateMetrics(data.metrics);
            renderRiskChart(data.charts.risk_distribution);
            renderAuthorChart(data.charts.top_authors);
            renderTable(data.findings);
            renderRemedyList(data.findings);
            
            if (data.filename) {
                document.getElementById('report-file').innerText = `📁 LOADED: ${data.filename}`;
            }
        } catch (err) {
            console.error('Error loading dashboard:', err);
        }
    }

    function updateMetrics(metrics) {
        document.getElementById('stat-total').innerText = metrics.total;
        document.getElementById('stat-critical').innerText = metrics.critical;
        document.getElementById('stat-cvss').innerText = metrics.avg_cvss;
        document.getElementById('stat-score').innerText = metrics.security_score + '%';
    }

    function renderTable(findings) {
        const tbody = document.getElementById('findings-table');
        tbody.innerHTML = findings.map(f => `
            <tr>
                <td><span class="risk-tag risk-${f.risk.toLowerCase()}">${f.risk}</span></td>
                <td>${f.cvss_score}</td>
                <td style="color: var(--accent)">${f.file}</td>
                <td>${f.reason}</td>
                <td>${f.author}</td>
            </tr>
        `).join('');
    }

    // --- Charts ---
    let riskChart, authorChart, anomalyChart;

    function renderRiskChart(dist) {
        const ctx = document.getElementById('riskChart').getContext('2d');
        if (riskChart) riskChart.destroy();
        riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(dist),
                datasets: [{
                    data: Object.values(dist),
                    backgroundColor: ['#ff0055', '#ff9900', '#00ccff', '#00ff41'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { color: '#8b949e' } } }
            }
        });
    }

    function renderAuthorChart(authors) {
        const ctx = document.getElementById('authorChart').getContext('2d');
        if (authorChart) authorChart.destroy();
        authorChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(authors),
                datasets: [{
                    label: 'Findings',
                    data: Object.values(authors),
                    backgroundColor: '#58a6ff',
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: '#30363d' }, ticks: { color: '#8b949e' } },
                    y: { grid: { display: false }, ticks: { color: '#8b949e' } }
                }
            }
        });
    }

    // --- AI Remediation ---
    function renderRemedyList(findings) {
        const list = document.getElementById('remedy-list');
        list.innerHTML = findings.slice(0, 10).map((f, i) => `
            <div class="finding-item" onclick="getRemediation(${i})">
                <div style="font-size: 0.7rem; color: #8b949e">${f.date}</div>
                <div style="font-weight: bold; margin: 4px 0;">${f.file.split('/').pop()}</div>
                <div class="risk-tag risk-${f.risk.toLowerCase()}" style="display:inline-block">${f.cvss_score}</div>
            </div>
        `).join('');
    }

    window.getRemediation = async (index) => {
        const finding = scanData.findings[index];
        const display = document.getElementById('remedy-content');
        
        display.innerHTML = `<div>ANALYZING FINDING...</div>`;
        
        try {
            const res = await fetch('/api/remediate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(finding)
            });
            const data = await res.json();
            
            display.innerHTML = `
                <div class="app-fade">
                    <h2 style="color: var(--neon-red); margin-bottom: 1rem;">${data.title}</h2>
                    <p style="margin-bottom: 1rem; color: #8b949e;">Severity: ${data.severity}</p>
                    
                    <h4 style="margin-top: 2rem;">RISK ANALYSIS:</h4>
                    <p style="margin: 0.5rem 0; line-height: 1.6;">${data.analysis}</p>
                    
                    <h4 style="margin-top: 2rem; color: var(--accent);">IMMEDIATE ACTIONS:</h4>
                    <div class="code-block">
                        <pre><code>${data.commands.join('\n')}</code></pre>
                        <button class="copy-btn" onclick="copyCode(this)">COPY</button>
                    </div>

                    <h4 style="margin-top: 2rem;">PREVENTION:</h4>
                    <ul style="margin: 0.5rem 0 0 1.5rem; line-height: 1.8;">
                        ${data.prevention.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
            `;
        } catch (err) {
            display.innerHTML = '<p style="color: var(--neon-red)">Error loading AI remediation</p>';
        }
    }

    window.copyCode = (btn) => {
        const code = btn.previousElementSibling.innerText;
        navigator.clipboard.writeText(code);
        btn.innerText = 'COPIED!';
        setTimeout(() => btn.innerText = 'COPY', 2000);
    }

    // --- Anomaly ---
    async function loadAnomalyData() {
        try {
            const res = await fetch('/api/anomaly');
            const data = await res.json();
            anomalyData = data;

            renderAnomalyChart(data);
            const tbody = document.getElementById('anomaly-table');
            tbody.innerHTML = data.filter(d => d.anomaly === -1).map(d => `
                <tr>
                    <td><span class="risk-tag risk-critical">ANOMALY</span></td>
                    <td style="color: var(--accent)">${d.file}</td>
                    <td>${d.entropy}</td>
                    <td>${d.reason}</td>
                </tr>
            `).join('');
        } catch (err) {
            console.error('Anomaly load error:', err);
        }
    }

    function renderAnomalyChart(data) {
        const ctx = document.getElementById('anomalyChart').getContext('2d');
        if (anomalyChart) anomalyChart.destroy();
        anomalyChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Normal',
                    data: data.filter(d => d.anomaly === 1).map(d => ({ x: d.entropy, y: d.len, r: d.cvss_score * 2 })),
                    backgroundColor: '#00ff41'
                }, {
                    label: 'Anomaly',
                    data: data.filter(d => d.anomaly === -1).map(d => ({ x: d.entropy, y: d.len, r: d.cvss_score * 3 })),
                    backgroundColor: '#ff0055'
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Entropy', color: '#8b949e' }, grid: { color: '#30363d' }, ticks: { color: '#8b949e' } },
                    y: { title: { display: true, text: 'File Length', color: '#8b949e' }, grid: { color: '#30363d' }, ticks: { color: '#8b949e' } }
                }
            }
        });
    }

    // --- Intel Charts ---
    function renderIntelCharts() {
        const currentData = { labels: ['Broken Access', 'Crypto Failures', 'Injection', 'Insecure Design'], scores: [95, 90, 85, 80] };
        const futureData = { labels: ['Auth Failures (A07)', 'Broken Access (A01)', 'AI Misconfig', 'LLM Leaks'], scores: [99, 95, 88, 92] };

        const renderChart = (id, data, color) => {
            new Chart(document.getElementById(id), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{ data: data.scores, backgroundColor: color }]
                },
                options: {
                    indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { grid: { display: false }, ticks: { color: '#8b949e' } }
                    }
                }
            });
        };

        renderChart('intelCurrentChart', currentData, '#58a6ff');
        renderChart('intelFutureChart', futureData, '#ff0055');
    }

    // Start
    loadDashboard();
});
