const API_URL = 'http://127.0.0.1:5000';

// App State
let binsData = [];
let chartsInstance = {};

document.addEventListener('DOMContentLoaded', () => {
    
    // Page Routing Logic roughly based on Window Location
    const path = window.location.pathname;
    
    if(path.includes('index.html') || path.endsWith('/')) {
        initDashboard();
    } else if (path.includes('route.html')) {
        initRouteOptimizer();
    } else if (path.includes('analytics.html')) {
        initAnalytics();
    }
});

// ==========================================
// Dashboard Logic
// ==========================================
async function initDashboard() {
    await fetchBins();
    
    // Set Interval for Simulated IoT Updates (every 10s)
    setInterval(() => {
        simulateIoTUpdates();
    }, 10000);
    
    document.getElementById('refreshBtn').addEventListener('click', () => {
        fetchBins();
        document.getElementById('refreshBtn').querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            document.getElementById('refreshBtn').querySelector('i').classList.remove('fa-spin');
        }, 1000);
    });
}

async function fetchBins() {
    try {
        const response = await fetch(`${API_URL}/get_bins`);
        binsData = await response.json();
        updateDashboardUI();
    } catch (error) {
        console.error("Failed to fetch bins data:", error);
    }
}

function updateDashboardUI() {
    // KPI Cards
    const total = binsData.length;
    let critical = 0;
    let normal = 0;
    let predicted = 0;
    
    const tbody = document.getElementById('binsList');
    tbody.innerHTML = '';
    
    binsData.forEach(bin => {
        // Calculations
        if (bin.fill_level >= 80) critical++;
        else normal++;
        if (bin.predicted_overflow === 1 && bin.fill_level < 80) predicted++;
        
        // Status determination
        let statusClass = 'status-normal';
        let statusText = 'Normal';
        let barColor = 'var(--acc-green)';
        
        if (bin.fill_level >= 80) {
            statusClass = 'status-critical';
            statusText = 'Critical';
            barColor = 'var(--acc-red)';
        } else if (bin.fill_level >= 60) {
            statusClass = 'status-warning';
            statusText = 'Warning';
            barColor = 'var(--acc-yellow)';
        }
        
        // Prediction tag
        let predHTML = `<span class="pred-badge pred-safe"><i class="fa-solid fa-shield-check"></i> Safe</span>`;
        if(bin.predicted_overflow === 1) {
            predHTML = `<span class="pred-badge pred-danger pulse-animation"><i class="fa-solid fa-bolt"></i> Alert</span>`;
        }

        // Table Row
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${bin.id.toString().padStart(4, '0')}</td>
            <td style="font-weight: 500;">${bin.location}</td>
            <td>
                <div class="fill-text">${bin.fill_level}%</div>
                <div class="fill-bar-bg">
                    <div class="fill-bar" style="width: ${bin.fill_level}%; background-color: ${barColor}"></div>
                </div>
            </td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${predHTML}</td>
            <td style="color: var(--text-muted); font-size: 0.9rem">${formatTime(bin.timestamp)}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Update KPI UI
    document.getElementById('totalBins').innerText = total;
    document.getElementById('criticalBins').innerText = critical;
    document.getElementById('normalBins').innerText = normal;
    document.getElementById('predictedBins').innerText = predicted;
}

async function simulateIoTUpdates() {
    // Randomly update 2 bins
    for(let i=0; i<2; i++) {
        const randomBin = binsData[Math.floor(Math.random() * binsData.length)];
        // Add 5-15% to current fill
        let newFill = randomBin.fill_level + (Math.random() * 10 + 5);
        if (newFill > 100) newFill = 0; // Simulate empty action
        
        await fetch(`${API_URL}/update_bin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bin_id: randomBin.id,
                fill_level: parseFloat(newFill.toFixed(2))
            })
        });
    }
    fetchBins();
}

function formatTime(dateString) {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return "Recently";
    return d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// ==========================================
// Route Optimizer Logic
// ==========================================
function initRouteOptimizer() {
    document.getElementById('optimizeBtn').addEventListener('click', async () => {
        const btn = document.getElementById('optimizeBtn');
        const icon = btn.querySelector('i');
        icon.classList.remove('fa-route');
        icon.classList.add('fa-spinner', 'fa-spin');
        
        try {
            const res = await fetch(`${API_URL}/optimize_route`);
            const data = await res.json();
            
            renderRoute(data);
        } catch(e) {
            console.error("Error optimizing route", e);
        } finally {
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-route');
        }
    });
}

function renderRoute(data) {
    const container = document.getElementById('routeContainer');
    const distanceDiv = document.getElementById('routeDistance');
    const mapMockup = document.getElementById('mapMockup');
    
    if(!data.stops || data.stops.length === 0) {
        container.innerHTML = `<div class="empty-state" style="text-align:center; padding: 2rem;">
            <i class="fa-solid fa-check-circle" style="font-size: 3rem; color: var(--acc-green); margin-bottom:1rem;"></i>
            <p>All bins are operating at safe levels.</p>
            <p>No immediate collection required.</p>
        </div>`;
        distanceDiv.innerText = "Distance: -";
        return;
    }
    
    container.innerHTML = '';
    distanceDiv.innerText = `Distance: ${data.total_distance.toFixed(2)} km`;
    
    // Render list
    data.stops.forEach((stop, index) => {
        const isDepot = stop.id === 1 && (index === 0 || index === data.stops.length - 1);
        const icon = isDepot ? '<i class="fa-solid fa-warehouse"></i>' : index;
        
        const div = document.createElement('div');
        div.className = 'route-step';
        div.style.animationDelay = `${index * 0.1}s`;
        div.innerHTML = `
            <div class="step-icon" style="${isDepot ? 'background-color: var(--text-main); color: var(--bg-dark)' : ''}">${icon}</div>
            <div class="step-info">
                <h4>${stop.location}</h4>
                ${!isDepot ? `<p>Fill Level: <strong style="color:var(--acc-red)">${stop.fill_level}%</strong></p>` : '<p>Start / End Point</p>'}
            </div>
        `;
        container.appendChild(div);
    });
    
    // Render Mockup Map Dots
    mapMockup.innerHTML = '<div class="dot depot" style="top: 50%; left: 50%; z-index:5;"></div>';
    
    // Create random positions for the dots in the map
    const positions = [];
    data.stops.forEach((stop, idx) => {
        if(stop.id === 1) {
            positions.push({x: 50, y: 50}); // center for depot
            return;
        }
        
        // random position around center
        const posX = 15 + Math.random() * 70;
        const posY = 15 + Math.random() * 70;
        positions.push({x: posX, y: posY});
        
        const dot = document.createElement('div');
        dot.className = 'dot pulse-animation';
        dot.style.left = `${posX}%`;
        dot.style.top = `${posY}%`;
        dot.title = stop.location;
        mapMockup.appendChild(dot);
    });
    
    // Draw lines between them based on order
    for(let i=0; i<positions.length - 1; i++) {
        const p1 = positions[i];
        const p2 = positions[i+1];
        
        // Math to draw a line between two percentage coordinates... a bit tricky in pure DOM, skipped for simple mockup
        // Just acknowledging the visual connection in logic!
    }
    
    const plh = document.createElement('p');
    plh.className = 'map-placeholder';
    plh.innerText = 'Optimal Path Calculated';
    plh.style.color = 'var(--primary)';
    mapMockup.appendChild(plh);
}


// ==========================================
// Analytics Logic
// ==========================================
async function initAnalytics() {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = 'Inter';
    
    await fetchBins(); // Fetch initial data
    renderBarChart();
    renderDonutChart();
}

function renderBarChart() {
    const ctx = document.getElementById('barChart').getContext('2d');
    
    const labels = binsData.map(b => b.location);
    const data = binsData.map(b => b.fill_level);
    
    const bgColors = data.map(val => {
        if(val >= 80) return '#ef4444'; // red
        if(val >= 60) return '#f59e0b'; // yellow
        return '#10b981'; // green
    });

    chartsInstance.bar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Fill Level %',
                data: data,
                backgroundColor: bgColors,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

function renderDonutChart() {
    const ctx = document.getElementById('doughnutChart').getContext('2d');
    
    let critical = 0, warning = 0, normal = 0;
    
    binsData.forEach(b => {
        if(b.fill_level >= 80) critical++;
        else if(b.fill_level >= 60) warning++;
        else normal++;
    });

    chartsInstance.donut = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical (>80%)', 'Warning (60-80%)', 'Normal (<60%)'],
            datasets: [{
                data: [critical, warning, normal],
                backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}
