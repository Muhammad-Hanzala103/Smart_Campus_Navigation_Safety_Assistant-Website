document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // Global Form Handlers
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();
            try {
                const res = await axios.post('/api/login', {
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value
                });
                if (res.data.status === 'ok') window.location.href = '/dashboard';
            } catch (err) {
                document.getElementById('error').innerText = 'Invalid credentials';
            }
        };
    }

    if (path === '/dashboard') loadDashboard();
    if (path === '/map') loadMapEditor();
    if (path === '/incidents') loadIncidents();
    if (path === '/bookings') loadBookings();
    if (path === '/users') loadUsers();
    if (path === '/analytics') loadAnalytics();
});

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

async function logout() {
    await axios.post('/api/logout');
    window.location.href = '/login';
}

// --- Dashboard ---
async function loadDashboard() {
    const [u, i, b] = await Promise.all([
        axios.get('/api/users'),
        axios.get('/api/incidents'),
        axios.get('/api/bookings')
    ]);
    document.getElementById('stat-users').innerText = u.data.length;
    document.getElementById('stat-incidents').innerText = i.data.filter(x => x.status === 'open').length;
    document.getElementById('stat-bookings').innerText = b.data.filter(x => x.status === 'pending').length;
}

// --- Map ---
async function loadMapEditor() {
    const container = document.getElementById('map-container');
    const { data } = await axios.get('/api/map');

    // Render Nodes
    data.nodes.forEach(n => {
        const el = document.createElement('div');
        el.className = 'map-node';
        el.style.left = n.x + 'px';
        el.style.top = n.y + 'px';
        el.title = n.name;
        el.onclick = (e) => { e.stopPropagation(); editNode(n); };
        container.appendChild(el);
    });

    // Click to add
    container.onclick = (e) => {
        if (e.target !== container && e.target.id !== 'map-image') return;
        const rect = container.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        openModal('node-modal');
        document.getElementById('n-x').value = x;
        document.getElementById('n-y').value = y;
        document.getElementById('n-id').value = '';
        document.getElementById('n-name').value = '';
        document.getElementById('n-desc').value = '';
    }

    document.getElementById('node-form').onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('n-id').value;
        const payload = {
            name: document.getElementById('n-name').value,
            description: document.getElementById('n-desc').value,
            x: document.getElementById('n-x').value,
            y: document.getElementById('n-y').value
        };
        if (id) await axios.put(`/api/map/nodes/${id}`, payload);
        else await axios.post('/api/map/nodes', payload);
        window.location.reload();
    }
}

function editNode(n) {
    openModal('node-modal');
    document.getElementById('n-id').value = n.id;
    document.getElementById('n-name').value = n.name;
    document.getElementById('n-desc').value = n.description;
    document.getElementById('n-x').value = n.x;
    document.getElementById('n-y').value = n.y;
}

async function deleteNode() {
    const id = document.getElementById('n-id').value;
    if (!id) return;
    if (confirm('Delete node?')) {
        await axios.delete(`/api/map/nodes/${id}`);
        window.location.reload();
    }
}

// --- Incidents ---
async function loadIncidents() {
    const { data } = await axios.get('/api/incidents');
    const tbody = document.getElementById('incidents-body');
    tbody.innerHTML = data.map(i => `
        <tr>
            <td>${i.category}</td>
            <td>${i.description}</td>
            <td>${i.status}</td>
            <td>${i.image_url ? `<a href="${i.image_url}" target="_blank">View</a>` : '-'}</td>
        </tr>
    `).join('');

    document.getElementById('incident-form').onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        await axios.post('/api/incidents', formData);
        window.location.reload();
    }
}

// --- Bookings ---
async function loadBookings() {
    const { data } = await axios.get('/api/bookings');
    const tbody = document.getElementById('bookings-body');
    tbody.innerHTML = data.map(b => `
        <tr>
            <td>${b.user_id}</td>
            <td>Room ${b.room_id}</td>
            <td>${b.start_time}</td>
            <td>${b.end_time}</td>
            <td class="${b.status === 'approved' ? 'text-success' : ''}">${b.status}</td>
            <td>
                ${b.status === 'pending' ? `
                <button class="btn btn-sm" onclick="setBooking(${b.id}, 'approved')">Aprv</button>
                <button class="btn btn-sm btn-danger" onclick="setBooking(${b.id}, 'rejected')">Rej</button>` : ''}
            </td>
        </tr>
    `).join('');
}

async function setBooking(id, status) {
    await axios.put(`/api/bookings/${id}/status`, { status });
    loadBookings();
}

// --- Users ---
async function loadUsers() {
    const { data } = await axios.get('/api/users');
    document.getElementById('users-body').innerHTML = data.map(u =>
        `<tr><td>${u.id}</td><td>${u.name}</td><td>${u.email}</td><td>${u.role}</td></tr>`
    ).join('');
}

// --- Analytics ---
async function loadAnalytics() {
    const { data } = await axios.get('/api/analytics');

    new Chart(document.getElementById('chart-incidents'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.incidents),
            datasets: [{ data: Object.values(data.incidents), backgroundColor: ['#007bff', '#dc3545', '#ffc107'] }]
        }
    });

    new Chart(document.getElementById('chart-bookings'), {
        type: 'bar',
        data: {
            labels: Object.keys(data.bookings),
            datasets: [{ label: 'Bookings', data: Object.values(data.bookings), backgroundColor: '#28a745' }]
        }
    });
}
