// MediScan Main Application Script

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initKeyboardShortcuts();
});

// Theme Management (Light / Dark)
function initTheme() {
    const savedTheme = localStorage.getItem('mediscan_theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    updateThemeIcon(savedTheme);

    const btn = document.getElementById('themeToggleBtn');
    if (btn) {
        btn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-bs-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', next);
            localStorage.setItem('mediscan_theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
}

// Keyboard Shortcuts (S = Search, D = Dashboard, R = Download Report, ? = Help)
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Do not trigger shortcuts while typing inside text fields or textareas
        const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
        if (['input', 'textarea', 'select'].includes(activeTag)) {
            return;
        }

        const key = e.key.toUpperCase();

        if (key === 'S') {
            e.preventDefault();
            const searchInput = document.getElementById('globalSearchInput') || document.getElementById('patientSearchInput');
            if (searchInput) searchInput.focus();
        } else if (key === 'D') {
            e.preventDefault();
            window.location.href = '/doctor/dashboard';
        } else if (key === 'R') {
            e.preventDefault();
            const reportBtn = document.getElementById('downloadReportBtn');
            if (reportBtn) reportBtn.click();
        } else if (e.key === '?') {
            e.preventDefault();
            const modalEl = document.getElementById('keyboardShortcutModal');
            if (modalEl) {
                const bsModal = new bootstrap.Modal(modalEl);
                bsModal.toggle();
            }
        }
    });
}

// Global User Logout Handler
function logoutUser() {
    fetch('/api/auth/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/login';
        })
        .catch(err => {
            console.error('Logout error:', err);
            window.location.href = '/login';
        });
}

// Helper to show bootstrap alerts
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) return;

    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show shadow-sm`;
    alertEl.innerHTML = `
        <i class="fa-solid fa-circle-info me-2"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.appendChild(alertEl);

    setTimeout(() => {
        if (alertEl.parentNode) alertEl.remove();
    }, 5000);
}
