function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    document.getElementById('btn-' + tabName).classList.add('active');
}

function filterModules() {
    const semSelect = document.getElementById("semester_select");
    const moduleSelect = document.getElementById("module_select");
    const selectedSem = semSelect.value;

    // Safety check if elements exist
    if (!semSelect || !moduleSelect) return;

    for (let i = 0; i < moduleSelect.options.length; i++) {
        const opt = moduleSelect.options[i];
        const modSem = opt.getAttribute("data-sem");
        if (!modSem) continue;

        if (selectedSem === "all" || modSem === selectedSem) {
            opt.style.display = "block";
            opt.disabled = false;
        } else {
            opt.style.display = "none";
            opt.disabled = true;
        }
    }
    moduleSelect.value = "";
}

function toggleRecurring() {
    const chk = document.getElementById("is_recurring");
    const endDiv = document.getElementById("recurring_end_div");
    const inp = document.getElementById("repeat_until");

    // Safety check
    if (!chk || !endDiv || !inp) return;

    if (chk.checked) {
        endDiv.style.display = "block";
        inp.required = true;
    } else {
        endDiv.style.display = "none";
        inp.required = false;
        inp.value = "";
    }
}

// Modal Functions
function openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.style.display = 'block';
}

function closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.style.display = 'none';
}

// Edit Lab
function openEditLabModal(btn) {
    const id = btn.getAttribute('data-id');
    const name = btn.getAttribute('data-name');
    const capacity = btn.getAttribute('data-capacity');
    const location = btn.getAttribute('data-location');
    const dept = btn.getAttribute('data-dept');

    document.getElementById('edit_lab_name').value = name;
    document.getElementById('edit_lab_capacity').value = capacity;
    document.getElementById('edit_lab_location').value = location;

    // Select Dept
    const deptSelect = document.getElementById('edit_lab_dept');
    if (deptSelect) deptSelect.value = dept;

    // Set Form Action
    document.getElementById('edit-lab-form').action = `/labs/update/${id}`;

    openModal('edit-lab-modal');
}

// Edit Module
function openEditModuleModal(btn) {
    const code = btn.getAttribute('data-code');
    const title = btn.getAttribute('data-title');
    const semester = btn.getAttribute('data-sem');
    const dept = btn.getAttribute('data-dept');

    document.getElementById('edit_mod_title').value = title;

    const semSelect = document.getElementById('edit_mod_sem');
    if (semSelect) semSelect.value = semester;

    const deptSelect = document.getElementById('edit_mod_dept');
    if (deptSelect) deptSelect.value = dept;

    // Set Form Action
    document.getElementById('edit-module-form').action = `/modules/update/${code}`;

    openModal('edit-module-modal');
}

// Edit Instructor
function openEditInstructorModal(btn) {
    const id = btn.getAttribute('data-id');
    const name = btn.getAttribute('data-name');
    const email = btn.getAttribute('data-email');
    const dept = btn.getAttribute('data-dept');
    const role = btn.getAttribute('data-role');
    const univ = btn.getAttribute('data-univ');
    const degree = btn.getAttribute('data-degree');
    const grad = btn.getAttribute('data-grad');
    const photo = btn.getAttribute('data-photo');

    document.getElementById('edit_inst_name').value = name;
    document.getElementById('edit_inst_email').value = email;
    document.getElementById('edit_inst_univ').value = univ;
    document.getElementById('edit_inst_degree').value = degree;
    document.getElementById('edit_inst_grad').value = grad;
    document.getElementById('edit_inst_photo').value = photo;

    const deptSelect = document.getElementById('edit_inst_dept');
    if (deptSelect) deptSelect.value = dept;

    const roleSelect = document.getElementById('edit_inst_role');
    if (roleSelect) roleSelect.value = role;

    // Set Form Action
    document.getElementById('edit-instructor-form').action = `/instructors/update/${id}`;

    openModal('edit-instructor-modal');
}

// Edit Booking
function openEditBookingModal(btn) {
    const id = btn.getAttribute('data-id');
    const date = btn.getAttribute('data-date');
    const start = btn.getAttribute('data-start');
    const end = btn.getAttribute('data-end');
    const module_code = btn.getAttribute('data-module');
    const lab_id = btn.getAttribute('data-lab');
    const instructor_id = btn.getAttribute('data-instructor');
    const practical = btn.getAttribute('data-practical');

    document.getElementById('edit_bk_date').value = date;

    // Time format adjustment (HH:MM:SS -> HH:MM)
    document.getElementById('edit_bk_start').value = start.substring(0, 5);
    document.getElementById('edit_bk_end').value = end.substring(0, 5);

    document.getElementById('edit_bk_module').value = module_code;
    document.getElementById('edit_bk_lab').value = lab_id;
    document.getElementById('edit_bk_instructor').value = instructor_id;
    document.getElementById('edit_bk_practical').value = (practical === 'None') ? '' : practical;

    // Set Form Action
    document.getElementById('edit-booking-form').action = `/bookings/update/${id}`;

    openModal('edit-booking-modal');
}

window.onclick = function (event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = 'none';
    }
}

// AJAX Calendar Loading
async function loadCalendar(year, month) {
    const container = document.getElementById('calendar-container');
    if (!container) return;

    // Show loading state (optional)
    container.style.opacity = '0.5';

    try {
        const response = await fetch(`/calendar/fragment?year=${year}&month=${month}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const html = await response.text();
        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading calendar:', error);
        container.innerHTML = '<div class="error">Failed to load calendar. Please try again.</div>';
    } finally {
        container.style.opacity = '1';
    }
}
