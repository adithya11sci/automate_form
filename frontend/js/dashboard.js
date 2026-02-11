/**
 * Dashboard Page Logic — Form filling, status polling, and stats
 */
let currentHistoryId = null;
let pollInterval = null;

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;

    await loadNavbar();
    await loadStats();

    // Toggle
    const toggle = document.getElementById('auto-submit-toggle');
    toggle?.addEventListener('click', () => {
        toggle.classList.toggle('active');
    });

    // Fill form
    document.getElementById('fill-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('form-url').value.trim();
        const autoSubmit = document.getElementById('auto-submit-toggle').classList.contains('active');
        const btn = document.getElementById('fill-btn');

        if (!url) {
            showToast('Please enter a Google Form URL', 'warning');
            return;
        }

        btn.innerHTML = '<span class="spinner"></span> Starting...';
        btn.disabled = true;

        try {
            const result = await api.fillForm(url, autoSubmit);
            currentHistoryId = result.id;
            showToast('Form filling started!', 'info');
            showStatusPanel(result);
            startPolling(result.id);
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.innerHTML = '⚡ Auto Fill';
            btn.disabled = false;
        }
    });
});

async function loadStats() {
    try {
        const history = await api.getFormHistory(0, 100);
        const total = history.total;
        const completed = history.items.filter(i => i.status === 'completed').length;
        const aiUsed = history.items.reduce((sum, i) => sum + (i.ai_answers_used || 0), 0);
        const filled = history.items.reduce((sum, i) => sum + (i.questions_filled || 0), 0);

        document.getElementById('stat-total').textContent = total;
        document.getElementById('stat-completed').textContent = completed;
        document.getElementById('stat-ai').textContent = aiUsed;
        document.getElementById('stat-filled').textContent = filled;
    } catch (e) {
        // Stats are optional, don't break the page
    }
}

function showStatusPanel(data) {
    const panel = document.getElementById('status-panel');
    panel.classList.add('visible');
    updateStatusUI(data);
}

function updateStatusUI(data) {
    // Badge
    const badge = document.getElementById('status-badge');
    badge.className = `status-badge ${data.status}`;
    badge.innerHTML = `<span class="pulse"></span> ${data.status.toUpperCase()}`;

    // Title
    document.getElementById('status-title').textContent = data.form_title || 'Processing...';

    // Progress
    const total = data.questions_detected || 1;
    const filled = data.questions_filled || 0;
    const pct = Math.round((filled / total) * 100);
    document.getElementById('progress-fill').style.width = `${pct}%`;
    document.getElementById('progress-text').textContent = `${filled}/${total} questions filled (${data.ai_answers_used || 0} AI-generated)`;

    // Log table
    const tbody = document.getElementById('log-body');
    tbody.innerHTML = '';

    if (data.fill_log && data.fill_log.length > 0) {
        data.fill_log.forEach(log => {
            const tr = document.createElement('tr');
            let sourceClass = 'profile';
            if (log.source?.includes('ai')) sourceClass = 'ai';
            else if (log.source?.includes('learned')) sourceClass = 'learned';
            else if (log.source?.includes('fallback')) sourceClass = 'fallback';

            tr.innerHTML = `
                <td title="${escapeHtml(log.question)}">${truncate(log.question, 40)}</td>
                <td>${log.field_type}</td>
                <td title="${escapeHtml(log.answer)}">${truncate(log.answer, 35)}</td>
                <td><span class="source-badge ${sourceClass}">${log.source}</span></td>
                <td>${log.status}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Error
    if (data.error_message) {
        document.getElementById('error-message').textContent = data.error_message;
        document.getElementById('error-row').style.display = 'flex';
    } else {
        document.getElementById('error-row').style.display = 'none';
    }
}

function startPolling(historyId) {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(async () => {
        try {
            const data = await api.getFormStatus(historyId);
            updateStatusUI(data);
            if (data.status === 'completed' || data.status === 'failed') {
                clearInterval(pollInterval);
                pollInterval = null;
                if (data.status === 'completed') {
                    showToast('Form filled successfully! ✨', 'success');
                } else {
                    showToast('Form filling failed: ' + (data.error_message || 'Unknown error'), 'error');
                }
                loadStats();
            }
        } catch (e) {
            clearInterval(pollInterval);
        }
    }, 2000);
}

async function loadNavbar() {
    try {
        const user = api.getUser();
        if (user) {
            document.getElementById('nav-username').textContent = user.username;
            document.getElementById('nav-avatar').textContent = user.username[0].toUpperCase();
        }
    } catch (e) { }
}

// Event: Logout
function logout() {
    api.clearToken();
    window.location.href = '/';
}

// Utilities
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, maxLen) {
    if (!text) return '';
    return text.length > maxLen ? text.substring(0, maxLen) + '...' : text;
}
