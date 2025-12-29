document.addEventListener('DOMContentLoaded', () => {
    // Determine current page from URL to run specific logic
    const path = window.location.pathname;

    if (path === '/dashboard') loadDashboard();
    if (path === '/map') initMapEditor();
    if (path === '/bookings') loadBookings();
    if (path === '/incidents') loadIncidents();
    if (path === '/users') loadUsers();
    if (path === '/analytics') loadAnalytics();
});

async function apiCall(url, method = 'GET', body = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(url, options);
    if (!res.ok) {
        if (res.status === 401) window.location.href = '/login';
        const err = await res.json();
        throw new Error(err.error || 'Request failed');
    }
    return res.json();
}

// --- Dashboard ---
async function loadDashboard() {
    try {
        const incidents = await apiCall('/api/analytics/incidents'); // Reuse for aggregate currently
        const bookings = await apiCall('/api/analytics/bookings');

        // Simple client-side aggregate
        let incidentCount = 0;
        Object.values(incidents).forEach(v => incidentCount += v);

        let pendingBookings = bookings['pending'] || 0;

        document.getElementById('stat-incidents').innerText = incidentCount;
        document.getElementById('stat-bookings').innerText = pendingBookings;

        const logs = await apiCall('/api/audit');
        const feed = document.getElementById('audit-feed');
        feed.innerHTML = logs.map(l => `<li>${l.timestamp.split('T')[0]} - <b>${l.action}</b>: ${l.details}</li>`).join('');
    } catch (e) { console.error(e); }
}

// --- Map Editor ---
async function initMapEditor() {
    const container = document.getElementById('map-container');
    const nodes = (await apiCall('/api/map')).nodes;

    nodes.forEach(node => {
        const el = document.createElement('div');
        el.className = 'map-node';
        el.style.left = node.x + 'px';
        el.style.top = node.y + 'px';
        el.title = node.name;
        el.onclick = (e) => { e.stopPropagation(); editNode(node); };
        container.appendChild(el);
    });

    // Simple add node on click
    container.onclick = (e) => {
        if (e.target !== container) return;
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        openNodeModal({ x, y });
    };
}

function openNodeModal(data) {
    const modal = document.getElementById('node-modal');
    modal.classList.add('active');
    document.getElementById('node-x').value = data.x;
    document.getElementById('node-y').value = data.y;
    document.getElementById('node-id').value = data.id || '';
    document.getElementById('node-name').value = data.name || '';
    document.getElementById('node-desc').value = data.description || '';
}

async function saveNode(e) {
    e.preventDefault();
    const id = document.getElementById('node-id').value;
    const data = {
        name: document.getElementById('node-name').value,
        description: document.getElementById('node-desc').value,
        x: document.getElementById('node-x').value,
        y: document.getElementById('node-y').value
    };

    try {
        if (id) await apiCall(`/api/map/nodes/${id}`, 'PUT', data);
        else await apiCall('/api/map/nodes', 'POST', data);
        location.reload();
    } catch (err) { alert(err.message); }
}

// --- Bookings ---
async function loadBookings() {
    const bookings = await apiCall('/api/bookings');
    const tbody = document.querySelector('#bookings-table tbody');
    tbody.innerHTML = bookings.map(b => `
        <tr>
            <td>${b.room_id}</td> <!-- In real app, fetch room name -->
            <td>${b.start.replace('T', ' ')}</td>
            <td>${b.end.replace('T', ' ')}</td>
            <td>${b.reason}</td>
            <td class="${b.status === 'approved' ? 'text-success' : b.status === 'rejected' ? 'text-danger' : ''}">${b.status}</td>
            <td>
                ${b.status === 'pending' ? `
                <button class="btn-sm btn-success" onclick="updateBooking(${b.id}, 'approved')">Approve</button>
                <button class="btn-sm btn-danger" onclick="updateBooking(${b.id}, 'rejected')">Reject</button>
                ` : ''}
            </td>
        </tr>
    `).join('');
}

async function updateBooking(id, status) {
    try {
        await apiCall(`/api/bookings/${id}/status`, 'PUT', { status });
        loadBookings();
    } catch (e) { alert(e.message); }
}

// --- Incidents ---
async function loadIncidents() {
    const list = await apiCall('/api/incidents');
    window.currentIncidents = list;
    const tbody = document.querySelector('#incidents-table tbody');
    tbody.innerHTML = list.map(i => {
        let aiHtml = '';
        if (i.ai_analyzed_at || i.ai_severity) {
            const badgeClass = i.ai_severity === 'HIGH' ? 'danger' : (i.ai_severity === 'MEDIUM' ? 'warning' : 'success');
            aiHtml = `<span class="badge badge-${badgeClass}" onclick="viewAIResult(${i.id})">${i.ai_severity || 'View'}</span>`;
        } else if (i.image) {
            aiHtml = `<button class="btn-sm" onclick="runAIAnalysis(${i.id}, this)">Run Analysis</button>`;
        } else {
            aiHtml = '<span class="text-muted">N/A</span>';
        }

        return `
        <tr>
            <td>${i.category}</td>
            <td>${i.description}</td>
            <td>${i.status}</td>
            <td>${aiHtml}</td>
            <td>${i.image ? `<a href="${i.image}" target="_blank">View</a>` : '-'}</td>
        </tr>
    `}).join('');
}

async function runAIAnalysis(id, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Running...';
    }
    try {
        const res = await apiCall('/api/incidents/analyze', 'POST', { incident_id: id });
        alert('Analysis Complete: ' + res.severity);
        loadIncidents();
    } catch (e) {
        alert(e.message);
        if (btn) {
            btn.disabled = false;
            btn.innerText = 'Run Analysis';
        }
    }
}

async function viewAIResult(id) {
    // We need to fetch details again or pass them.
    // Since list endpoint didn't include full labels, we might need to fetch single incident or parse from list if we update list to return them.
    // Let's assume list returns them or we fetch analysis (simpler: update list API to return ai fields).
    // Wait, get_incidents in api.py currently returns: id, description, category, x, y, status, image, created_at.
    // I NEED TO UPDATE api.py get_incidents to return ai fields!
    // Otherwise I can't show them without another call. 
    // I will use a separate call or pass data if available. 
    // Let's use `runAIAnalysis` endpoint which returns full structure, but that re-runs it? No, that's POST.
    // I should probably just update `get_incidents` to return the new fields.
    // Or I can just fetch the incident details if I had a route for it.
    // `api.py` doesn't have `GET /api/incidents/<id>`.
    // QUICK FIX: Update `api.py` to Include AI data in list.

    // Validating current step: I will implement the JS assuming data is there, AND THEN update `api.py` to ensure it is there.
    // Just finding the item from the list we already fetched?
    // `loadIncidents` fetched `list`. I can store `list` globally or recall it.
    // Better: Update `api.py` `get_incidents` first.

    // For now, I'll write the JS to use a global lookup or refetch.
    // Let's use a quick ugly trick: find it in the DOM or refetch list?
    // Let's just alert for now or implement a "get details" if strictly needed.
    // Actually, I can just update `api.py` concurrently.

    // Let's stick to simple View:
    // We will assume `i` has `ai_labels` etc.
    // But `loadIncidents` has local `list`.
    // I'll make logic to find it or just pass data to viewAIResult?
    // Strings in HTML attributes are messy.
    // I'll update `loadIncidents` to attach data to the row or something.
    // Or just fetch all again.

    // Better: `viewAIResult` finds the incident in a cache.
    // I'll add `window.currentIncidents = list;` in `loadIncidents`.

    const incident = window.currentIncidents.find(x => x.id === id);
    if (!incident) return;

    const labels = typeof incident.ai_labels === 'string' ? JSON.parse(incident.ai_labels || '[]') : (incident.ai_labels || []);
    const rec = incident.ai_recommendation || 'No recommendation';
    const time = incident.ai_analyzed_at || 'N/A';

    const html = `
        <p><b>Severity:</b> <span class="badge">${incident.ai_severity}</span></p>
        <p><b>Analyzed At:</b> ${time}</p>
        <p><b>Recommendation:</b> ${rec}</p>
        <h4>Detections:</h4>
        <ul>
            ${labels.map(l => `<li>${l.name} (${(l.confidence * 100).toFixed(0)}%)</li>`).join('')}
        </ul>
    `;
    document.getElementById('ai-result-content').innerHTML = html;
    document.getElementById('ai-modal').classList.add('active');
}

// --- Analytics ---
async function loadAnalytics() {
    const incData = await apiCall('/api/analytics/incidents');
    const bookData = await apiCall('/api/analytics/bookings');

    new Chart(document.getElementById('incidentsChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(incData),
            datasets: [{ label: 'Incidents by Category', data: Object.values(incData), backgroundColor: '#3498db' }]
        }
    });

    new Chart(document.getElementById('bookingsChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(bookData),
            datasets: [{ label: 'Booking Status', data: Object.values(bookData), backgroundColor: ['#2ecc71', '#e74c3c', '#f1c40f'] }]
        }
    });
}
