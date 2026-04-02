document.addEventListener('DOMContentLoaded', () => {
    updateNavbar(); 

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                username: document.getElementById('reg-name').value,
                email: document.getElementById('reg-email').value,
                password: document.getElementById('reg-password').value,
                role: document.getElementById('reg-role').value
            };

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();

                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                    
                    const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
                    modal.hide();
                    registerForm.reset();

                    updateNavbar();
                } else {
                    alert('Error: ' + (result.message || 'Registration failed'));
                }
            } catch (err) {
                console.error('Registration error:', err);
            }
        });
    }

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = {
                email: loginForm.querySelector('input[type="email"]').value,
                password: loginForm.querySelector('input[type="password"]').value
            };

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();

                if (response.ok) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                    window.location.reload(); 
                } else {
                    alert('Login failed: ' + (result.message || 'Invalid credentials'));
                }
            } catch (err) {
                console.error('Login error:', err);
            }
        });
    }
});

function updateNavbar() {
    const userData = localStorage.getItem('user');
    
    if (userData) {
        const user = JSON.parse(userData);
        const authContainer = document.querySelector('.d-flex.gap-2'); 

        if (authContainer) {
            authContainer.innerHTML = `
                <div class="dropdown">
                    <button class="btn btn-outline-light btn-sm dropdown-toggle shadow-sm" type="button" data-bs-toggle="dropdown">
                         ${user.name}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow">
                        <li><span class="dropdown-item-text text-muted small">Role: ${user.role}</span></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#" id="logout-btn">Logout</a></li>
                    </ul>
                </div>
            `;

            document.getElementById('logout-btn').onclick = (e) => {
                e.preventDefault();
                localStorage.removeItem('user');
                window.location.reload();
            };
        }
    }
}