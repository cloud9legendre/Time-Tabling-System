// Tab Navigation
function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    document.getElementById('btn-' + tabName).classList.add('active');
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
    }
}

// AJAX Calendar Loading
async function loadCalendar(year, month) {
    const container = document.getElementById('calendar-container');
    if (!container) return;

    container.style.opacity = '0.5';

    try {
        const response = await fetch(`/calendar/fragment?year=${year}&month=${month}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading calendar:', error);
        container.innerHTML = '<div class="error" style="text-align:center; padding:20px;">Failed to load calendar. Please try again.</div>';
    } finally {
        container.style.opacity = '1';
    }
}
