function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span> <span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Function to handle URL params on page load (legacy support or initial load)
function checkUrlToasts() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('success')) {
        showToast(urlParams.get('success'), 'success');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname + window.location.hash);
    }
    if (urlParams.has('error')) {
        showToast(urlParams.get('error'), 'error');
        window.history.replaceState({}, document.title, window.location.pathname + window.location.hash);
    }
}

document.addEventListener("DOMContentLoaded", checkUrlToasts);
