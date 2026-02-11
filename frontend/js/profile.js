/**
 * Profile Page Logic — Load, edit, and save profile data.
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    await loadNavbar();
    await loadProfile();

    // Save profile
    document.getElementById('profile-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('save-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Saving...';
        btn.disabled = true;

        try {
            const data = getFormData();
            await api.saveProfile(data);
            showToast('Profile saved successfully!', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
});

async function loadProfile() {
    try {
        const profile = await api.getProfile();
        if (profile) {
            setField('full_name', profile.full_name);
            setField('register_number', profile.register_number);
            setField('department', profile.department);
            setField('year', profile.year);
            setField('email', profile.email);
            setField('phone', profile.phone);
            setField('gender', profile.gender);
            setField('college_name', profile.college_name);
            setField('address', profile.address);
            setField('skills', profile.skills);
            setField('interests', profile.interests);
            setField('bio', profile.bio);
        }
    } catch (e) {
        // Profile may not exist yet, that's okay
    }
}

function getFormData() {
    return {
        full_name: getField('full_name'),
        register_number: getField('register_number'),
        department: getField('department'),
        year: getField('year'),
        email: getField('email'),
        phone: getField('phone'),
        gender: getField('gender'),
        college_name: getField('college_name'),
        address: getField('address'),
        skills: getField('skills'),
        interests: getField('interests'),
        bio: getField('bio'),
        extra_fields: {},
    };
}

function setField(name, value) {
    const el = document.getElementById(name);
    if (el) el.value = value || '';
}

function getField(name) {
    const el = document.getElementById(name);
    return el ? el.value.trim() : '';
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

function logout() {
    api.clearToken();
    window.location.href = '/';
}
