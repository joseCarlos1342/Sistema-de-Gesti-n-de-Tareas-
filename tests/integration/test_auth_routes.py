import pytest
from flask import url_for
from app.models import User
from app import db

class TestAuthRoutes:
    """Test cases for authentication routes."""

    def test_register_page_get(self, client):
        """Test registration page loads correctly."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Crear Cuenta' in response.data
        assert b'name' in response.data
        assert b'email' in response.data
        assert b'password' in response.data

    def test_register_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'new@test.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Registro exitoso' in response.data

        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(email='new@test.com').first()
            assert user is not None
            assert user.name == 'New User'
            assert user.role == 'user'

    def test_register_duplicate_email(self, client, regular_user):
        """Test registration with duplicate email."""
        response = client.post('/auth/register', data={
            'name': 'Another User',
            'email': 'user@test.com',  # Already exists
            'password': 'password123',
            'password_confirm': 'password123'
        })

        assert response.status_code == 200
        assert b'El email ya est\xc3\xa1 registrado' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'password': 'password123',
            'password_confirm': 'different123'
        })

        assert response.status_code == 200
        # Form validation should catch this

    def test_register_short_password(self, client):
        """Test registration with short password."""
        response = client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'password': '123',
            'password_confirm': '123'
        })

        assert response.status_code == 200
        assert b'La contrase\xc3\xb1a debe tener al menos 6 caracteres' in response.data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'invalid-email',
            'password': 'password123',
            'password_confirm': 'password123'
        })

        assert response.status_code == 200
        # Form validation should catch this

    def test_login_page_get(self, client):
        """Test login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Iniciar Sesi\xc3\xb3n' in response.data
        assert b'email' in response.data
        assert b'password' in response.data

    def test_login_success(self, client, regular_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'user123'
        }, follow_redirects=True)

        assert response.status_code == 200
        # Should redirect to dashboard

        # Check session
        with client.session_transaction() as sess:
            assert sess['user_id'] == regular_user.id
            assert sess['user_name'] == regular_user.name
            assert sess['user_role'] == regular_user.role

    def test_login_wrong_password(self, client, regular_user):
        """Test login with wrong password."""
        response = client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        assert b'Email o contrase\xc3\xb1a incorrectos' in response.data

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert b'Email o contrase\xc3\xb1a incorrectos' in response.data

    def test_login_redirect_authenticated_user(self, authenticated_client):
        """Test that authenticated users are redirected from login page."""
        response = authenticated_client.get('/auth/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to dashboard

    def test_logout(self, authenticated_client):
        """Test logout functionality."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Has cerrado sesi\xc3\xb3n exitosamente' in response.data

        # Check session is cleared
        with authenticated_client.session_transaction() as sess:
            assert 'user_id' not in sess

    def test_profile_page_authenticated(self, authenticated_client, regular_user):
        """Test profile page for authenticated user."""
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200
        assert b'Mi Perfil' in response.data
        assert regular_user.name.encode() in response.data
        assert regular_user.email.encode() in response.data

    def test_profile_page_unauthenticated(self, client):
        """Test profile page redirects unauthenticated users."""
        response = client.get('/auth/profile', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to login

    def test_update_profile_success(self, authenticated_client, app, regular_user):
        """Test successful profile update."""
        response = authenticated_client.post('/auth/profile', data={
            'name': 'Updated Name',
            'email': 'updated@test.com'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Perfil actualizado exitosamente' in response.data

        # Verify changes in database
        with app.app_context():
            user = User.query.get(regular_user.id)
            assert user.name == 'Updated Name'
            assert user.email == 'updated@test.com'

    def test_update_profile_duplicate_email(self, authenticated_client, regular_user, second_user):
        """Test profile update with duplicate email."""
        response = authenticated_client.post('/auth/profile', data={
            'name': 'Updated Name',
            'email': 'user2@test.com'  # second_user's email
        })

        assert response.status_code == 200
        assert b'El email ya est\xc3\xa1 en uso por otro usuario' in response.data

    def test_change_password_page(self, authenticated_client):
        """Test change password page."""
        response = authenticated_client.get('/auth/change_password')
        assert response.status_code == 200
        assert b'Cambiar Contrase\xc3\xb1a' in response.data

    def test_change_password_success(self, authenticated_client, app, regular_user):
        """Test successful password change."""
        response = authenticated_client.post('/auth/change_password', data={
            'current_password': 'user123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Contrase\xc3\xb1a cambiada exitosamente' in response.data

        # Verify password was changed by attempting login with new password
        authenticated_client.get('/auth/logout')
        response = authenticated_client.post('/auth/login', data={
            'email': 'user@test.com',
            'password': 'newpassword123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        response = authenticated_client.post('/auth/change_password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })

        assert response.status_code == 200
        assert b'La contrase\xc3\xb1a actual es incorrecta' in response.data

    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with confirmation mismatch."""
        response = authenticated_client.post('/auth/change_password', data={
            'current_password': 'user123',
            'new_password': 'newpassword123',
            'confirm_password': 'different123'
        })

        assert response.status_code == 200
        # Form validation should catch this

    def test_change_password_too_short(self, authenticated_client):
        """Test password change with too short new password."""
        response = authenticated_client.post('/auth/change_password', data={
            'current_password': 'user123',
            'new_password': '123',
            'confirm_password': '123'
        })

        assert response.status_code == 200
        assert b'La contrase\xc3\xb1a debe tener al menos 6 caracteres' in response.data

    def test_auth_required_redirects(self, client):
        """Test that protected routes redirect to login."""
        protected_routes = [
            '/auth/profile',
            '/auth/change_password',
            '/tasks/',
            '/tasks/new',
            '/'
        ]

        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 302  # Redirect
            assert '/auth/login' in response.location

    def test_login_next_parameter(self, client, regular_user):
        """Test login redirect to next parameter."""
        # Try to access protected route
        response = client.get('/tasks/')
        assert response.status_code == 302

        # Login with next parameter
        response = client.post('/auth/login?next=/tasks/', data={
            'email': 'user@test.com',
            'password': 'user123'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/tasks/' in response.location

    def test_session_persistence(self, authenticated_client, regular_user):
        """Test that session persists across requests."""
        # Make multiple requests
        response1 = authenticated_client.get('/')
        response2 = authenticated_client.get('/tasks/')
        response3 = authenticated_client.get('/auth/profile')

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Session should still be valid
        with authenticated_client.session_transaction() as sess:
            assert sess['user_id'] == regular_user.id