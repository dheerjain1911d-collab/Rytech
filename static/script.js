document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const nav = document.getElementById('mainNav');
    if (nav) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }
        });
    }

    // Soil auto-fill
    const soilSelect = document.getElementById('soil_type');
    if (soilSelect) {
        soilSelect.addEventListener('change', function() {
            const option = this.options[this.selectedIndex];
            if (option.dataset.n) {
                document.getElementById('N').value = option.dataset.n;
                document.getElementById('P').value = option.dataset.p;
                document.getElementById('K').value = option.dataset.k;
            }
        });
    }

    // Form submission
    const cropForm = document.getElementById('cropForm');
    if (cropForm) {
        cropForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                N: parseFloat(document.getElementById('N').value),
                P: parseFloat(document.getElementById('P').value),
                K: parseFloat(document.getElementById('K').value),
                temperature: parseFloat(document.getElementById('temperature').value),
                humidity: parseFloat(document.getElementById('humidity').value),
                ph: parseFloat(document.getElementById('ph').value),
                rainfall: parseFloat(document.getElementById('rainfall').value),
                area: parseFloat(document.getElementById('area').value),
                location: document.getElementById('location').value
            };

            const submitBtn = cropForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
            submitBtn.disabled = true;

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (data.ml_recommendations) {
                    displayResults(data.ml_recommendations);
                    if (data.rule_recommendations && data.rule_recommendations.length) {
                        displayResults(data.rule_recommendations, 'Rule-Based Recommendations', true);
                    }
                    const profitEl = document.getElementById('profit');
                    if (profitEl) {
                        profitEl.innerHTML = `<span class="profit-badge">💰 Estimated Avg Profit: ₹${data.avg_profit_estimate.toLocaleString()}</span>`;
                    }
                    populateComparisonTable(data.ml_recommendations, data.rule_recommendations);
                } else if (data.recommendations) {
                    displayResults(data.recommendations);
                    populateComparisonTable(data.recommendations, null);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error getting recommendations. Check console.');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // Real weather API button
    const getWeatherBtn = document.getElementById('getWeather');
    if (getWeatherBtn) {
        getWeatherBtn.addEventListener('click', async () => {
            const originalText = getWeatherBtn.innerHTML;
            getWeatherBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i>Fetching weather...';
            getWeatherBtn.disabled = true;

            const applyDemoData = (reason) => {
                const demoTemp = 25 + Math.random() * 10;
                const demoHum = 60 + Math.random() * 30;
                const demoRain = 50 + Math.random() * 200;
                document.getElementById('temperature').value = demoTemp.toFixed(1);
                document.getElementById('humidity').value = demoHum.toFixed(1);
                document.getElementById('rainfall').value = demoRain.toFixed(0);
                document.getElementById('location').value = 'Hyderabad, Telangana';
                console.warn('Weather fallback used:', reason);
            };

            const flashInputs = () => {
                ['temperature','humidity','rainfall','location'].forEach(id => {
                    const el = document.getElementById(id);
                    if (!el) return;
                    el.style.borderColor = '#22c55e';
                    el.style.boxShadow = '0 0 0 4px rgba(34, 197, 94, 0.2)';
                    setTimeout(() => {
                        el.style.borderColor = '';
                        el.style.boxShadow = '';
                    }, 1200);
                });
            };

            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser. Using demo data.');
                applyDemoData('geolocation unsupported');
                flashInputs();
                getWeatherBtn.innerHTML = originalText;
                getWeatherBtn.disabled = false;
                return;
            }

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    try {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const apiKey = '68c14b75890e0a76849afbd2540a09da';
                        const response = await fetch(
                            `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`
                        );

                        if (!response.ok) {
                            const errData = await response.json().catch(() => ({}));
                            throw new Error(errData.message || `HTTP ${response.status}`);
                        }

                        const data = await response.json();
                        if (!data.main) {
                            throw new Error('Invalid weather data received');
                        }

                        document.getElementById('temperature').value = data.main.temp.toFixed(1);
                        document.getElementById('humidity').value = data.main.humidity.toFixed(1);
                        document.getElementById('rainfall').value = data.rain ? (data.rain['1h'] || data.rain['3h'] || 0) : 0;
                        document.getElementById('location').value = data.name + ', ' + data.sys.country;
                        flashInputs();
                    } catch (err) {
                        console.error('Weather API error:', err);
                        alert('Weather API error: ' + err.message + '. Using demo data.');
                        applyDemoData(err.message);
                        flashInputs();
                    } finally {
                        getWeatherBtn.innerHTML = originalText;
                        getWeatherBtn.disabled = false;
                    }
                },
                (err) => {
                    let msg = 'Location access denied.';
                    if (err.code === 1) msg = 'Location permission denied. Please allow location access or use manual input.';
                    else if (err.code === 2) msg = 'Location unavailable. Using demo data.';
                    else if (err.code === 3) msg = 'Location request timed out. Using demo data.';
                    alert(msg);
                    applyDemoData('geolocation error code ' + err.code);
                    flashInputs();
                    getWeatherBtn.innerHTML = originalText;
                    getWeatherBtn.disabled = false;
                },
                { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 }
            );
        });
    }

    // OTP QR code generation (client-side, fixes missing to_base64_qr filter)
    const qrContainer = document.getElementById('qrContainer');
    const qrUri = document.getElementById('qrUri');
    if (qrContainer && qrUri && typeof QRCode !== 'undefined') {
        new QRCode(qrContainer, {
            text: qrUri.value,
            width: 180,
            height: 180,
            colorDark: '#064e3b',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });
    }

    const fertilizerForm = document.getElementById('fertilizerForm');
    if (fertilizerForm) {
        fertilizerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const payload = {
                N: parseFloat(document.getElementById('fertN').value),
                P: parseFloat(document.getElementById('fertP').value),
                K: parseFloat(document.getElementById('fertK').value),
                area: parseFloat(document.getElementById('fertArea').value)
            };

            const submitBtn = fertilizerForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculating...';
            submitBtn.disabled = true;

            try {
                const response = await fetch('/fertilizers/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                displayFertilizerResults(data);
            } catch (err) {
                console.error('Fertilizer calculation error:', err);
                alert('Could not generate fertilizer recommendations.');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});

function toggleComparisonTable() {
    const wrap = document.getElementById('comparisonTableWrap');
    if (!wrap) return;
    wrap.classList.toggle('hidden');
}

function populateComparisonTable(mlRecs, ruleRecs) {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const allRows = [];

    (mlRecs || []).forEach(r => {
        const waterKL = r.water ? (r.water / 1000).toFixed(0) : '-';
        let fert = '-';
        let nextCrop = '-';
        if (r.suitability) {
            const fertMatch = r.suitability.match(/Fert:\s*([^|]+)/);
            if (fertMatch) fert = fertMatch[1].trim();
            const nextMatch = r.suitability.match(/Next:\s*([^|]+)/);
            if (nextMatch) nextCrop = nextMatch[1].trim();
        }
        allRows.push({
            name: r.name || '-',
            type: 'ML',
            score: typeof r.score === 'number' ? r.score : 0,
            water: waterKL,
            env: r.env_score !== undefined ? r.env_score : '-',
            fertilizer: fert,
            nextCrop: nextCrop
        });
    });

    (ruleRecs || []).forEach(r => {
        allRows.push({
            name: r.name || '-',
            type: 'Rule',
            score: typeof r.score === 'number' ? r.score : 0,
            water: '-',
            env: '-',
            fertilizer: '-',
            nextCrop: '-'
        });
    });

    if (allRows.length === 0) return;

    // Determine best values
    const numericScores = allRows.map(r => r.score).filter(v => typeof v === 'number');
    const numericWater = allRows.map(r => parseFloat(r.water)).filter(v => !isNaN(v));
    const numericEnv = allRows.map(r => (typeof r.env === 'number' ? r.env : null)).filter(v => v !== null);

    const bestScore = numericScores.length ? Math.max(...numericScores) : null;
    const bestWater = numericWater.length ? Math.min(...numericWater) : null; // lowest water usage is best
    const bestEnv = numericEnv.length ? Math.max(...numericEnv) : null;

    allRows.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.style.animationDelay = `${index * 0.05}s`;
        tr.className = 'animate-in';

        const scoreClass = (row.score === bestScore) ? 'best-value' : '';
        const waterClass = (parseFloat(row.water) === bestWater) ? 'best-value' : '';
        const envClass = (row.env === bestEnv) ? 'best-value' : '';

        const typeBadgeClass = row.type === 'ML' ? 'ml' : 'rule';

        tr.innerHTML = `
            <td><strong>${row.name}</strong></td>
            <td><span class="type-badge ${typeBadgeClass}">${row.type}</span></td>
            <td class="col-score"><span class="${scoreClass}">${row.score.toFixed(1)}%</span></td>
            <td class="col-water"><span class="${waterClass}">${row.water}</span></td>
            <td class="col-env"><span class="${envClass}">${row.env}</span></td>
            <td>${row.fertilizer}</td>
            <td>${row.nextCrop}</td>
        `;
        tbody.appendChild(tr);
    });
}

function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        grid: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
        text: isDark ? '#9ca3af' : '#6b7280',
        tooltipBg: isDark ? '#1f2937' : '#ffffff',
        tooltipText: isDark ? '#f9fafb' : '#1a1a1a'
    };
}

function displayFertilizerResults(data) {
    const results = document.getElementById('fertResults');
    const deficits = document.getElementById('fertDeficits');
    const list = document.getElementById('fertList');
    if (!results || !deficits || !list) return;

    const d = data.deficits || {};
    deficits.innerHTML = `
        <div class="fert-deficit-grid">
            <div class="fert-deficit-item"><strong>N Deficit:</strong> ${(d.N || 0).toFixed(1)}</div>
            <div class="fert-deficit-item"><strong>P Deficit:</strong> ${(d.P || 0).toFixed(1)}</div>
            <div class="fert-deficit-item"><strong>K Deficit:</strong> ${(d.K || 0).toFixed(1)}</div>
        </div>
    `;

    const recs = data.recommendations || [];
    list.innerHTML = recs.map(rec => `
        <div class="rec-item">
            <div class="rec-header">
                <div class="rec-name">${rec.fertilizer}</div>
            </div>
            <div class="rec-meta">
                <strong>Purpose:</strong> ${rec.purpose}<br>
                <strong>Suggested Quantity:</strong> ${rec.quantity_kg} kg
            </div>
        </div>
    `).join('');

    results.classList.remove('hidden');
}

function displayResults(recommendations, title = '', isAppend = false) {
    const recList = document.getElementById('recList');
    const resultsDiv = document.getElementById('results');
    if (!recList || !resultsDiv) return;

    if (!isAppend) {
        recList.innerHTML = '';
    }

    if (title) {
        const titleDiv = document.createElement('div');
        titleDiv.className = 'rec-section-title';
        titleDiv.textContent = title;
        titleDiv.style.cssText = 'font-weight:700;font-size:1rem;color:var(--text-primary);margin:1.5rem 0 0.75rem;padding-bottom:0.5rem;border-bottom:1px solid var(--border-card);';
        if (!isAppend) {
            recList.appendChild(titleDiv);
        } else {
            recList.appendChild(titleDiv);
        }
    }

    recommendations.forEach((rec, index) => {
        const div = document.createElement('div');
        div.className = 'rec-item animate-in';
        div.style.animationDelay = `${index * 0.1}s`;

        const rank = index + 1;
        const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : rank === 3 ? 'rank-3' : '';
        const badgeHtml = rank <= 3 ? `<span class="rec-badge ${rankClass}">#${rank}</span>` : '';

        const scoreVal = typeof rec.score === 'number' ? rec.score : 0;
        const metaParts = [];
        if (rec.suitability) metaParts.push(rec.suitability);
        if (rec.water) metaParts.push(`💧 Water: ${(rec.water/1000).toFixed(0)}K L/ha`);
        if (rec.env_score !== undefined) metaParts.push(`🌿 Env Score: ${rec.env_score}/10`);
        if (rec.fertilizer) metaParts.push(`💚 Fert: ${rec.fertilizer}`);
        if (rec.soil_health) metaParts.push(`🔄 ${rec.soil_health}`);
        if (rec.shap) metaParts.push(`📊 SHAP: ${rec.shap}`);
        if (typeof rec.estimated_profit === 'number') {
            metaParts.push(`💰 Est Profit: ₹${Math.round(rec.estimated_profit).toLocaleString()}`);
        }

        const metaHtml = metaParts.length ? `<div class="rec-meta">${metaParts.join(' &nbsp;|&nbsp; ')}</div>` : '';

        div.innerHTML = `
            <div class="rec-header">
                <div class="rec-name">${rec.name}</div>
                ${badgeHtml}
            </div>
            <div class="rec-score-row">
                <span class="rec-score-text">${scoreVal.toFixed(1)}%</span>
                <div class="rec-progress-bg">
                    <div class="rec-progress-fill" data-width="${Math.min(scoreVal, 100)}"></div>
                </div>
            </div>
            ${metaHtml}
        `;
        recList.appendChild(div);

        // Animate progress bar after a small delay
        setTimeout(() => {
            const fill = div.querySelector('.rec-progress-fill');
            if (fill) fill.style.width = fill.dataset.width + '%';
        }, 100 + index * 100);
    });

    resultsDiv.classList.remove('hidden');
    resultsDiv.classList.add('animate-in');

    // Chart
    const theme = getThemeColors();
    let chart = Chart.getChart('scoreChart');
    if (chart) chart.destroy();

    const ctx = document.getElementById('scoreChart');
    if (!ctx) return;

    const labels = recommendations.map(r => r.name);
    const dataPoints = recommendations.map(r => typeof r.score === 'number' ? r.score : 0);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Suitability Score (%)',
                data: dataPoints,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.85)',
                    'rgba(5, 150, 105, 0.85)',
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(52, 211, 153, 0.85)',
                    'rgba(20, 184, 166, 0.85)',
                    'rgba(6, 182, 212, 0.85)'
                ],
                borderColor: [
                    '#22c55e', '#059669', '#10b981', '#34d399', '#14b8a6', '#06b6d4'
                ],
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    borderColor: 'rgba(52, 211, 153, 0.3)',
                    borderWidth: 1,
                    cornerRadius: 10,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: theme.text,
                        font: { family: "'Poppins', sans-serif", size: 11 }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: theme.grid },
                    ticks: {
                        color: theme.text,
                        font: { family: "'Poppins', sans-serif", size: 11 },
                        callback: function(value) { return value + '%'; }
                    }
                }
            }
        }
    });
}

