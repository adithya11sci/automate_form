/**
 * Auth Page Logic — Login / Signup with auto-login detection
 */
document.addEventListener('DOMContentLoaded', () => {
    // Auto-redirect if already authenticated
    if (api.isAuthenticated()) {
        api.getMe().then(() => {
            window.location.href = '/dashboard';
        }).catch(() => {
            api.clearToken();
        });
    }

    // Tab switching
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${target}-form`).classList.add('active');
        });
    });

    // Login
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Signing in...';
        btn.disabled = true;

        try {
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value;

            const data = await api.login(username, password);
            api.setToken(data.access_token);
            api.setUser({ id: data.user_id, username: data.username });

            showToast(`Welcome back, ${data.username}!`, 'success');
            setTimeout(() => window.location.href = '/dashboard', 600);
        } catch (err) {
            showToast(err.message, 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });

    // Signup
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Creating account...';
        btn.disabled = true;

        try {
            const username = document.getElementById('signup-username').value.trim();
            const email = document.getElementById('signup-email').value.trim();
            const password = document.getElementById('signup-password').value;
            const confirmPassword = document.getElementById('signup-confirm').value;

            if (password !== confirmPassword) {
                throw new Error('Passwords do not match');
            }
            if (password.length < 6) {
                throw new Error('Password must be at least 6 characters');
            }

            const data = await api.signup(username, email, password);
            api.setToken(data.access_token);
            api.setUser({ id: data.user_id, username: data.username });

            showToast('Account created! Set up your profile.', 'success');
            setTimeout(() => window.location.href = '/profile', 600);
        } catch (err) {
            showToast(err.message, 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
});
