/**
 * History Page Logic — View past form fills and details.
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    await loadNavbar();
    await loadHistory();
});

async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div style="text-align:center;padding:2rem;"><div class="spinner spinner-lg" style="margin:0 auto;"></div></div>';

    try {
        const data = await api.getFormHistory(0, 50);

        if (data.items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <h3>No forms filled yet</h3>
                    <p>Go to the dashboard and paste a Google Form link to get started!</p>
                    <a href="/dashboard" class="btn btn-primary" style="margin-top:1rem;">Go to Dashboard</a>
                </div>
            `;
            return;
        }

        container.innerHTML = '';

        data.items.forEach(item => {
            const statusColors = {
                completed: 'var(--success)',
                failed: 'var(--error)',
                filling: 'var(--info)',
                pending: 'var(--warning)',
            };
            const statusBg = {
                completed: 'var(--success-bg)',
                failed: 'var(--error-bg)',
                filling: 'var(--info-bg)',
                pending: 'var(--warning-bg)',
            };
            const icons = {
                completed: '✅',
                failed: '❌',
                filling: '⏳',
                pending: '🕐',
            };

            const div = document.createElement('div');
            div.className = 'history-item';
            div.onclick = () => showDetail(item);
            div.innerHTML = `
                <div class="history-icon" style="background:${statusBg[item.status] || 'var(--bg-glass)'};color:${statusColors[item.status] || 'inherit'};">
                    ${icons[item.status] || '📄'}
                </div>
                <div class="history-info">
                    <div class="history-title">${escapeHtml(item.form_title || 'Untitled Form')}</div>
                    <div class="history-meta">
                        <span>${timeAgo(item.created_at)}</span>
                        <span style="color:${statusColors[item.status]}">${item.status}</span>
                        ${item.auto_submitted ? '<span>✓ Auto-submitted</span>' : ''}
                    </div>
                </div>
                <div class="history-stats">
                    <div class="history-stat">
                        <div class="history-stat-value">${item.questions_detected}</div>
                        <div class="history-stat-label">Detected</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-value">${item.questions_filled}</div>
                        <div class="history-stat-label">Filled</div>
                    </div>
                    <div class="history-stat">
                        <div class="history-stat-value" style="color:var(--accent-secondary)">${item.ai_answers_used}</div>
                        <div class="history-stat-label">AI Used</div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Error loading history</h3><p>${err.message}</p></div>`;
    }
}

function showDetail(item) {
    const modal = document.getElementById('detail-modal');
    const content = document.getElementById('detail-content');

    let logHtml = '';
    if (item.fill_log && item.fill_log.length > 0) {
        logHtml = `
            <table class="log-table" style="margin-top:1rem;">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Type</th>
                        <th>Answer</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    ${item.fill_log.map(log => {
            let sourceClass = 'profile';
            if (log.source?.includes('ai')) sourceClass = 'ai';
            else if (log.source?.includes('learned')) sourceClass = 'learned';
            else if (log.source?.includes('fallback')) sourceClass = 'fallback';
            return `<tr>
                            <td>${escapeHtml(log.question)}</td>
                            <td>${log.field_type}</td>
                            <td>${escapeHtml(log.answer)}</td>
                            <td><span class="source-badge ${sourceClass}">${log.source}</span></td>
                        </tr>`;
        }).join('')}
                </tbody>
            </table>
        `;
    }

    content.innerHTML = `
        <h2 style="margin-bottom:0.5rem;">${escapeHtml(item.form_title || 'Untitled Form')}</h2>
        <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem;">
            <a href="${escapeHtml(item.form_url)}" target="_blank" style="word-break:break-all;">${escapeHtml(item.form_url)}</a>
        </p>
        <div class="stats-grid" style="margin-bottom:1rem;">
            <div class="stat-card">
                <div class="stat-icon purple">📝</div>
                <div><div class="stat-value">${item.questions_detected}</div><div class="stat-label">Detected</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon green">✓</div>
                <div><div class="stat-value">${item.questions_filled}</div><div class="stat-label">Filled</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-icon yellow">🤖</div>
                <div><div class="stat-value">${item.ai_answers_used}</div><div class="stat-label">AI Used</div></div>
            </div>
        </div>
        ${item.error_message ? `<div style="padding:12px;background:var(--error-bg);border-radius:8px;color:var(--error);margin-bottom:1rem;">⚠ ${escapeHtml(item.error_message)}</div>` : ''}
        ${logHtml}
        <div style="text-align:right;margin-top:1.5rem;">
            <button class="btn btn-secondary" onclick="closeModal()">Close</button>
        </div>
    `;

    modal.classList.add('visible');
}

function closeModal() {
    document.getElementById('detail-modal').classList.remove('visible');
}

// Close on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeModal();
    }
});

async function loadNavbar() {
    try {
        const user = api.getUser();
        if (user) {
            document.getElementById('nav-username').textContent = user.username;
            document.getElementById('nav-avatar').textContent = user.username[0].toUpperCase();
        }
    } catch (e) { }
}

function logout() {
    api.clearToken();
    window.location.href = '/';
}

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
