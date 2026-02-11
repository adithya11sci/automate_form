/**
 * API Client — Centralized HTTP client for all backend calls.
 */
const API_BASE = '';  // Same origin

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
    }

    getUser() {
        const data = localStorage.getItem('auth_user');
        return data ? JSON.parse(data) : null;
    }

    setUser(user) {
        localStorage.setItem('auth_user', JSON.stringify(user));
    }

    isAuthenticated() {
        return !!this.token;
    }

    async request(method, path, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const opts = { method, headers };
        if (body) {
            opts.body = JSON.stringify(body);
        }

        const res = await fetch(`${API_BASE}${path}`, opts);

        let data;
        try {
            data = await res.json();
        } catch (e) {
            data = { detail: `Server error (${res.status})` };
        }

        if (!res.ok) {
            if (res.status === 401) {
                this.clearToken();
                window.location.href = '/';
            }
            throw new Error(data.detail || `Request failed with status ${res.status}`);
        }
        return data;

    }

    // Auth
    signup(username, email, password) {
        return this.request('POST', '/api/auth/signup', { username, email, password });
    }

    login(username, password) {
        return this.request('POST', '/api/auth/login', { username, password });
    }

    getMe() {
        return this.request('GET', '/api/auth/me');
    }

    // Profile
    getProfile() {
        return this.request('GET', '/api/profile/');
    }

    saveProfile(data) {
        return this.request('POST', '/api/profile/', data);
    }

    updateProfile(data) {
        return this.request('PUT', '/api/profile/', data);
    }

    // Forms
    fillForm(formUrl, autoSubmit) {
        return this.request('POST', '/api/forms/fill', { form_url: formUrl, auto_submit: autoSubmit });
    }

    getFormStatus(historyId) {
        return this.request('GET', `/api/forms/status/${historyId}`);
    }

    getFormHistory(skip = 0, limit = 20) {
        return this.request('GET', `/api/forms/history?skip=${skip}&limit=${limit}`);
    }

    getMappings() {
        return this.request('GET', '/api/forms/mappings');
    }

    deleteMapping(mappingId) {
        return this.request('DELETE', `/api/forms/mappings/${mappingId}`);
    }
}

// Singleton
const api = new ApiClient();

// ─── Toast Notifications ────────────────────────────────────
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 4000);
}

// ─── Auth Guard ─────────────────────────────────────────────
function requireAuth() {
    if (!api.isAuthenticated()) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// ─── Time formatting ────────────────────────────────────────
function timeAgo(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}
