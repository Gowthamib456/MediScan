/**
 * MediScan Main Client-Side JavaScript
 * Verifies backend REST API health via GET /api/health and updates UI badges.
 */

document.addEventListener('DOMContentLoaded', () => {
  const badge = document.getElementById('api-status-badge');
  const jsonBox = document.getElementById('health-json-box');
  const refreshBtn = document.getElementById('btn-refresh-health');
  const connectionTag = document.getElementById('connection-status-tag');

  async function checkApiHealth() {
    if (badge) {
      badge.className = 'badge bg-outline-warning border text-warning px-3 py-2';
      badge.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Connecting...';
    }

    try {
      const response = await fetch('/api/health');
      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }
      const data = await response.json();

      if (badge) {
        badge.className = 'badge bg-success text-white px-3 py-2 shadow-sm';
        badge.innerHTML = '<i class="fa-solid fa-circle-check me-1"></i> API Operational';
      }

      if (connectionTag) {
        connectionTag.className = 'badge bg-success';
        connectionTag.textContent = 'API Connected';
      }

      if (jsonBox) {
        jsonBox.textContent = JSON.stringify(data, null, 2);
      }
    } catch (err) {
      console.error('API Health Check Error:', err);

      if (badge) {
        badge.className = 'badge bg-danger text-white px-3 py-2 shadow-sm';
        badge.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-1"></i> API Offline';
      }

      if (connectionTag) {
        connectionTag.className = 'badge bg-danger';
        connectionTag.textContent = 'API Connection Error';
      }

      if (jsonBox) {
        jsonBox.textContent = JSON.stringify({
          status: "error",
          message: "Unable to reach MediScan Flask Backend API at /api/health",
          details: err.message
        }, null, 2);
      }
    }
  }

  // Execute initial health check
  checkApiHealth();

  if (refreshBtn) {
    refreshBtn.addEventListener('click', (e) => {
      e.preventDefault();
      checkApiHealth();
    });
  }
});
