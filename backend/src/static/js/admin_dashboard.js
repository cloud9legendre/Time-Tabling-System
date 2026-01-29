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

    if (chk.checked) {
        endDiv.style.display = "block";
        inp.required = true;
    } else {
        endDiv.style.display = "none";
        inp.required = false;
        inp.value = "";
    }
}
