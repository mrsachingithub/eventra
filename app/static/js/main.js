const apiBaseUrl = '/api/auth';
const eventsApiUrl = '/api/events';
const bookingsApiUrl = '/api/bookings';

document.addEventListener('DOMContentLoaded', () => {
    // --- Auth Forms ---
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleLogin(new FormData(loginForm));
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleRegister(new FormData(registerForm));
        });
    }

    // --- Organizer Forms ---
    const createVenueForm = document.getElementById('createVenueForm');
    if (createVenueForm) {
        createVenueForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleCreateVenue(new FormData(createVenueForm));
        });
    }

    const createEventForm = document.getElementById('createEventForm');
    if (createEventForm) {
        loadVenuesForDropdown();
        createEventForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleCreateEvent(new FormData(createEventForm));
        });
    }

    // --- Page Loads ---
    const path = window.location.pathname;

    if (path === '/organizer/dashboard') {
        loadOrganizerEvents();
        loadGlobalOrganizerStats();
    } else if (path === '/admin/dashboard') {
        loadAdminStats();
        loadAdminUsers();
    } else if (path === '/' || path === '/index.html') {
        loadPublicEvents();
    } else if (path.startsWith('/events/')) {
        // Event ID is available as global const EVENT_ID from template
        if (typeof EVENT_ID !== 'undefined') {
            loadEventDetails(EVENT_ID);
        }
    } else if (path === '/my-bookings') {
        loadMyBookings();
    }

    checkAuth();
});

// --- Admin Handlers ---
async function loadAdminStats() {
    try {
        const response = await authFetch('/api/admin/stats', { method: 'GET' });
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('totalUsers').textContent = stats.users;
            document.getElementById('totalEvents').textContent = stats.events;
            document.getElementById('totalRevenue').textContent = `$${stats.revenue}`;
        }
    } catch (err) { console.error(err); }
}

// --- Auth Handlers ---
async function handleLogin(formData) {
    const data = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${apiBaseUrl}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (response.ok) {
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('refresh_token', result.refresh_token);
            localStorage.setItem('role', result.role);
            alert('Login successful!');
            window.location.href = result.role === 'customer' ? '/' : `/${result.role}/dashboard`;
        } else {
            alert(result.msg);
        }
    } catch (error) { console.error(error); }
}

async function handleRegister(formData) {
    const data = Object.fromEntries(formData.entries());
    try {
        const response = await fetch(`${apiBaseUrl}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (response.ok) {
            alert('Registration successful! Please login.');
            window.location.href = '/login';
        } else {
            alert(result.msg);
        }
    } catch (error) { console.error(error); }
}

// --- Organizer Handlers ---
async function handleCreateVenue(formData) {
    const data = Object.fromEntries(formData.entries());
    try {
        const response = await authFetch(`${eventsApiUrl}/venues`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            alert('Venue Created!');
            const role = localStorage.getItem('role');
            window.location.href = role === 'admin' ? '/admin/dashboard' : '/organizer/dashboard';
        } else {
            const res = await response.json();
            alert(res.msg);
        }
    } catch (err) { console.error(err); }
}

async function handleCreateEvent(formData) {
    const data = Object.fromEntries(formData.entries());
    try {
        const response = await authFetch(`${eventsApiUrl}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            alert('Event Created!');
            const role = localStorage.getItem('role');
            window.location.href = role === 'admin' ? '/admin/dashboard' : '/organizer/dashboard';
        } else {
            const res = await response.json();
            alert(res.msg);
        }
    } catch (err) { console.error(err); }
}

async function loadVenuesForDropdown() {
    const select = document.getElementById('venue_id');
    try {
        const response = await authFetch(`${eventsApiUrl}/venues`, { method: 'GET' });
        if (response.ok) {
            const venues = await response.json();
            venues.forEach(v => {
                const option = document.createElement('option');
                option.value = v.id;
                option.textContent = v.name;
                select.appendChild(option);
            });
        }
    } catch (err) { console.error(err); }
}

async function loadGlobalOrganizerStats() {
    try {
        const response = await authFetch(`${eventsApiUrl}/organizer/stats`, { method: 'GET' });
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('globalEvents').textContent = stats.total_events;
            document.getElementById('globalTickets').textContent = stats.total_tickets_sold;
            document.getElementById('globalRevenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
        }
    } catch (err) { console.error(err); }
}

async function loadOrganizerEvents() {
    const list = document.getElementById('eventsList');
    try {
        const response = await authFetch(`${eventsApiUrl}/organizer`, { method: 'GET' });
        if (response.ok) {
            const events = await response.json();
            list.innerHTML = '';
            if (events.length === 0) list.innerHTML = '<p>No events found.</p>';
            events.forEach(e => {
                const div = document.createElement('div');
                div.className = 'event-card';
                div.innerHTML = `
                    <h3>${e.title}</h3>
                    <p>Date: ${new Date(e.date_time).toLocaleString()}</p>
                    <p>Status: <span style="color: ${e.status === 'Active' ? '#2ecc71' : '#e74c3c'}">${e.status}</span></p>
                    <button class="btn-primary manage-btn" onclick="openManageModal(${e.id}, '${e.title}', '${e.status}')" style="margin-top: 10px;">Manage</button>
                `;
                list.appendChild(div);
            });
        }
    } catch (err) { console.error(err); }
}

// Global scope for onclick access (cleaner would be event delegation, but this is MVP)
window.openManageModal = async (id, title, status) => {
    const modal = document.getElementById('manageEventModal');
    const titleEl = document.getElementById('manageEventTitle');
    const statusSpan = document.getElementById('currentStatus');
    const toggleBtn = document.getElementById('toggleStatusBtn');

    titleEl.textContent = `Manage: ${title}`;
    statusSpan.textContent = status;
    statusSpan.style.color = status === 'Active' ? '#2ecc71' : '#e74c3c';

    // Configure Toggle Button
    if (status === 'Active') {
        toggleBtn.textContent = 'Cancel Event';
        toggleBtn.style.background = '#e74c3c';
        toggleBtn.onclick = () => updateEventStatus(id, 'Cancelled');
    } else {
        toggleBtn.textContent = 'Re-activate Event';
        toggleBtn.style.background = '#2ecc71';
        toggleBtn.onclick = () => updateEventStatus(id, 'Active');
    }

    modal.style.display = 'flex';

    // Load Data
    await loadEventAnalytics(id);
    await loadEventBookings(id);

    // Close Logic
    const span = modal.querySelector(".close");
    span.onclick = () => modal.style.display = "none";
    window.onclick = (event) => {
        if (event.target == modal) modal.style.display = "none";
    }
};

async function loadEventAnalytics(id) {
    try {
        const response = await authFetch(`${eventsApiUrl}/${id}/analytics`);
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('statCapacity').textContent = stats.total_capacity;
            document.getElementById('statSold').textContent = stats.sold_tickets;
            document.getElementById('statRemaining').textContent = stats.remaining_tickets;
            document.getElementById('statRevenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
        }
    } catch (err) { console.error(err); }
}

async function loadEventBookings(id) {
    const list = document.getElementById('eventBookingsList');
    list.innerHTML = '<p>Loading...</p>';
    try {
        const response = await authFetch(`${eventsApiUrl}/${id}/bookings`);
        if (response.ok) {
            const bookings = await response.json();
            list.innerHTML = '';
            if (bookings.length === 0) list.innerHTML = '<p>No bookings yet.</p>';

            bookings.forEach(b => {
                const div = document.createElement('div');
                div.className = 'booking-item';
                div.innerHTML = `
                   <div style="flex: 1;">
                       <h4 style="margin: 0; color: var(--primary-color);">${b.customer_name} (${b.customer_email})</h4>
                       <p style="margin: 5px 0; font-size: 0.9rem; color: #ccc;">Seats: ${b.seats}</p>
                       <p style="margin: 0; font-size: 0.8rem; color: #888;">Ordered: ${new Date(b.date).toLocaleString()}</p>
                   </div>
                   <div style="text-align: right;">
                       <p style="font-weight: bold; margin-bottom: 5px;">$${b.total_amount}</p>
                       <span class="ticket-status ${b.status}">${b.status}</span>
                   </div>
                `;
                list.appendChild(div);
            });
        }
    } catch (err) { console.error(err); }
}

async function updateEventStatus(id, newStatus) {
    if (!confirm(`Are you sure you want to change status to ${newStatus}?`)) return;

    try {
        const response = await authFetch(`${eventsApiUrl}/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            alert(`Event ${newStatus}!`);
            document.getElementById('manageEventModal').style.display = 'none';
            loadOrganizerEvents(); // Refresh list
        } else {
            const res = await response.json();
            alert(res.msg);
        }
    } catch (err) { console.error(err); }
}

// --- Customer Handlers ---
async function loadPublicEvents() {
    const list = document.getElementById('publicEventsList');
    if (!list) return;
    try {
        const response = await fetch(`${eventsApiUrl}/`, { method: 'GET' });
        if (response.ok) {
            const events = await response.json();
            list.innerHTML = '';
            if (events.length === 0) list.innerHTML = '<p>No upcoming events.</p>';
            events.forEach(e => {
                const div = document.createElement('div');
                div.className = 'event-card';
                div.innerHTML = `
                    <h3>${e.title}</h3>
                    <p>${e.venue} | $${e.base_price}</p>
                    <p>${new Date(e.date_time).toLocaleString()}</p>
                    <button onclick="handleTicketClick(${e.id})" class="btn-primary">Book Tickets</button>
                `;
                list.appendChild(div);
            });
        }
    } catch (err) { console.error(err); }
}

let selectedSeats = new Set();
let basePrice = 0;

async function loadEventDetails(eventId) {
    const infoDiv = document.getElementById('eventInfo');
    const seatMap = document.getElementById('seatMap');
    const bookBtn = document.getElementById('bookBtn');

    try {
        // Fetch Event Info
        const eventRes = await fetch(`${eventsApiUrl}/${eventId}`);
        const eventData = await eventRes.json();

        infoDiv.innerHTML = `
            <h1>${eventData.title}</h1>
            <p>${eventData.description || ''}</p>
            <p><strong>Venue:</strong> ${eventData.venue_name}, ${eventData.venue_address}</p>
            <p><strong>Date:</strong> ${new Date(eventData.date_time).toLocaleString()}</p>
        `;
        basePrice = eventData.base_price;

        // Fetch Seats
        const seatRes = await fetch(`${bookingsApiUrl}/${eventId}/seats`);
        const seats = await seatRes.json();

        seatMap.innerHTML = '';

        // Group by Row
        const seatsByRow = {};
        seats.forEach(seat => {
            if (!seatsByRow[seat.row]) {
                seatsByRow[seat.row] = [];
            }
            seatsByRow[seat.row].push(seat);
        });

        // Render Rows
        Object.keys(seatsByRow).sort().forEach(rowLabel => {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'seat-row';

            // Optional: Row Label
            const labelSpan = document.createElement('span');
            labelSpan.className = 'row-label';
            labelSpan.innerText = rowLabel;
            rowDiv.appendChild(labelSpan);

            seatsByRow[rowLabel].sort((a, b) => a.number - b.number).forEach(seat => {
                const div = document.createElement('div');
                div.className = `seat ${seat.status}`;
                div.dataset.id = seat.id;
                div.dataset.price = seat.price;
                div.dataset.row = seat.row;
                div.dataset.number = seat.number;
                div.title = `${seat.row}${seat.number} - $${seat.price}`;
                div.innerText = seat.number; // Just number in the box

                if (seat.status === 'available') {
                    div.addEventListener('click', () => toggleSeat(div));
                }
                rowDiv.appendChild(div);
            });
            seatMap.appendChild(rowDiv);
        });

        bookBtn.addEventListener('click', () => {
            if (bookBtn.disabled) return;
            const modal = document.getElementById('paymentModal');
            const total = document.getElementById('totalPrice').innerText;
            document.getElementById('modalTotal').innerText = total;
            modal.style.display = 'flex';
        });

        // Modal Close Logic
        const modal = document.getElementById('paymentModal');
        const span = document.getElementsByClassName("close")[0];
        if (span) {
            span.onclick = function () {
                modal.style.display = "none";
            }
        }
        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }

        // Handle Payment Form
        const paymentForm = document.getElementById('paymentForm');
        // Remove old listener if exists (tough in vanilla JS withoutnamed func, but simple add is okay for now as page reloads)
        paymentForm.onsubmit = async (e) => {
            e.preventDefault();
            await bookSelectedSeats(eventId);
        };

    } catch (err) { console.error(err); }
}

function toggleSeat(seatDiv) {
    const id = seatDiv.dataset.id;
    if (selectedSeats.has(id)) {
        selectedSeats.delete(id);
        seatDiv.classList.remove('selected');
        console.log(`Deselected seat ${id}`);
    } else {
        selectedSeats.add(id);
        seatDiv.classList.add('selected');
        console.log(`Selected seat ${id}`);
    }
    updateSummary();
}

function updateSummary() {
    const count = selectedSeats.size;
    console.log(`Selected count: ${count}`);
    const selectedElements = Array.from(document.querySelectorAll('.seat.selected'));
    const total = selectedElements.reduce((sum, el) => sum + parseFloat(el.dataset.price), 0);

    const labels = selectedElements.map(el => `${el.dataset.row}${el.dataset.number}`).join(', ');
    document.getElementById('selectedSeatsList').innerText = labels ? `(${labels})` : '';

    document.getElementById('selectedCount').textContent = count;
    document.getElementById('totalPrice').textContent = total.toFixed(2);

    // Enable/Disable button
    const btn = document.getElementById('bookBtn');
    btn.disabled = count === 0;
    console.log(`Button disabled? ${btn.disabled}`);
}

async function bookSelectedSeats(eventId) {
    if (selectedSeats.size === 0) return;

    if (!localStorage.getItem('access_token')) {
        alert('Please login to book tickets.');
        window.location.href = '/login';
        return;
    }

    const statusDiv = document.getElementById('paymentStatus'); // Not in DOM yet but robust to add if needed, otherwise alert

    try {
        // Step 1: Lock Seats
        const lockResponse = await authFetch(`${bookingsApiUrl}/lock`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_id: eventId,
                seat_ids: Array.from(selectedSeats)
            })
        });

        const lockResult = await lockResponse.json();
        if (!lockResponse.ok) {
            alert(lockResult.msg);
            document.getElementById('paymentModal').style.display = 'none';
            return;
        }

        // Step 2: Simulate Payment processing time
        const payBtn = document.querySelector('#paymentForm button[type="submit"]');
        const originalText = payBtn.textContent;
        payBtn.textContent = 'Processing Payment...';
        payBtn.disabled = true;

        setTimeout(async () => {
            // Step 3: Confirm Booking
            const confirmResponse = await authFetch(`${bookingsApiUrl}/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    booking_id: lockResult.booking_id
                })
            });

            const confirmResult = await confirmResponse.json();

            if (confirmResponse.ok) {
                // Success
                window.location.href = `/api/bookings/ticket/${confirmResult.booking_id}`;
            } else {
                alert('Payment/Confirmation Failed: ' + confirmResult.msg);
                payBtn.textContent = originalText;
                payBtn.disabled = false;
            }
        }, 1500); // 1.5s delay for effect

    } catch (err) { console.error(err); }
}

async function loadMyBookings() {
    const list = document.getElementById('myBookingsList');
    try {
        const response = await authFetch(`${bookingsApiUrl}/my`, { method: 'GET' });
        if (response.ok) {
            const bookings = await response.json();
            list.innerHTML = '';
            bookings.forEach(b => {
                const div = document.createElement('div');
                div.className = 'booking-item';
                div.className = 'booking-item';
                div.innerHTML = `
                    <div class="ticket-left">
                        <div>
                            <h3 class="ticket-title">${b.event_title}</h3>
                            <p class="ticket-info"><i class="fas fa-calendar-alt"></i> ${new Date(b.date).toLocaleString()}</p>
                            <div class="ticket-seats">Seats: ${b.seats}</div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <strong>Total: $${b.total_amount}</strong>
                        </div>
                    </div>
                    <div class="ticket-right">
                        <i class="fas fa-qrcode ticket-qr"></i>
                        <span class="ticket-status ${b.status}">${b.status}</span>
                    </div>
                `;
                list.appendChild(div);
            });
        }
    } catch (err) { console.error(err); }
}

// --- Common ---
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const navUl = document.querySelector('nav ul');

    // Reset Nav
    navUl.innerHTML = '<li><a href="/">Home</a></li>';

    if (token) {
        const role = localStorage.getItem('role');

        if (role === 'organizer') {
            const li = document.createElement('li');
            li.innerHTML = '<a href="/organizer/dashboard">Dashboard</a>';
            navUl.appendChild(li);
        } else if (role === 'admin') {
            const li = document.createElement('li');
            li.innerHTML = '<a href="/admin/dashboard">Admin</a>';
            navUl.appendChild(li);
        } else {
            const li = document.createElement('li');
            li.innerHTML = '<a href="/my-bookings">My Bookings</a>';
            navUl.appendChild(li);
        }

        const logoutLi = document.createElement('li');
        logoutLi.innerHTML = '<a href="#" id="logoutBtn">Logout</a>';
        navUl.appendChild(logoutLi);

        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    } else {
        const loginLi = document.createElement('li');
        loginLi.innerHTML = '<a href="/login">Login</a>';
        navUl.appendChild(loginLi);

        const registerLi = document.createElement('li');
        registerLi.innerHTML = '<a href="/register">Register</a>';
        navUl.appendChild(registerLi);
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('role');
    window.location.href = '/login';
}

async function authFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    if (!token) {
        // Return mock 401 response to prevent crashes
        return {
            ok: false,
            status: 401,
            json: async () => ({ msg: "Please login first" })
        };
    }

    options.headers = options.headers || {};
    options.headers['Authorization'] = `Bearer ${token}`;

    let response = await fetch(url, options);

    if (response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
            const refreshRes = await fetch(`${apiBaseUrl}/refresh`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${refreshToken}` }
            });
            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('access_token', data.access_token);
                token = data.access_token;
                options.headers['Authorization'] = `Bearer ${token}`;
                response = await fetch(url, options);
            } else {
                logout();
            }
        } else {
            logout();
        }
    }
    return response;
}

// --- Admin Page Logic ---
window.showAdminTab = function (tab) {
    document.querySelectorAll('.admin-section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    if (tab === 'users') {
        document.getElementById('usersSection').style.display = 'block';
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        loadAdminUsers();
    } else {
        document.getElementById('eventsSection').style.display = 'block';
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        loadAdminEvents();
    }
};

async function loadAdminUsers() {
    try {
        const response = await authFetch('/api/admin/users');
        if (response.ok) {
            const users = await response.json();
            const tbody = document.getElementById('allUsersTable');
            tbody.innerHTML = '';
            users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.id}</td>
                    <td>${u.username}</td>
                    <td>${u.email}</td>
                    <td>
                        <select onchange="updateUserRole(${u.id}, this.value)" class="form-select">
                            <option value="customer" ${u.role === 'customer' ? 'selected' : ''}>Customer</option>
                            <option value="organizer" ${u.role === 'organizer' ? 'selected' : ''}>Organizer</option>
                            <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                        </select>
                    </td>
                    <td>
                         <button class="btn-danger btn-sm" onclick="alert('Delete not implemented yet')">Delete</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) { console.error(err); }
}

async function loadAdminEvents() {
    try {
        const response = await authFetch('/api/admin/events');
        if (response.ok) {
            const events = await response.json();
            const tbody = document.getElementById('allEventsTable');
            tbody.innerHTML = '';
            events.forEach(e => {
                const tr = document.createElement('tr');
                // Status color
                let statusColor = '#2ecc71';
                if (e.status === 'Cancelled') statusColor = '#e74c3c';
                if (e.status === 'Suspended') statusColor = '#f39c12';

                tr.innerHTML = `
                    <td>${e.id}</td>
                    <td>${e.title}</td>
                    <td>${e.organizer}</td>
                    <td style="color: ${statusColor}; font-weight: bold;">${e.status}</td>
                    <td>$${e.revenue}</td>
                    <td>
                        ${e.status === 'Active' ?
                        `<button class="btn-warning btn-sm" onclick="updateEventStatus(${e.id}, 'Suspended')">Suspend</button>` :
                        `<button class="btn-secondary btn-sm" disabled>${e.status}</button>`
                    }
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) { console.error(err); }
}

window.updateUserRole = async (userId, newRole) => {
    if (!confirm('Change user role?')) return;
    try {
        const res = await authFetch(`/api/admin/users/${userId}/role`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: newRole })
        });
        if (res.ok) alert('Role updated');
        else {
            const data = await res.json();
            alert(data.msg || 'Failed');
        }
        loadAdminUsers();
    } catch (err) { console.error(err); }
};

window.updateEventStatus = async (eventId, newStatus) => {
    if (!confirm(`Change status to ${newStatus}?`)) return;
    try {
        const res = await authFetch(`/api/admin/events/${eventId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) alert('Event status updated');
        else {
            const data = await res.json();
            alert(data.msg || 'Failed');
        }
        loadAdminEvents();
    } catch (err) { console.error(err); }
};

window.handleTicketClick = (eventId) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
    } else {
        window.location.href = `/events/${eventId}`;
    }
};


