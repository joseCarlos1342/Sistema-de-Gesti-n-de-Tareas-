import pytest
from werkzeug.security import check_password_hash
from app.services.auth_service import AuthService
from app.models import User
from app import db

class TestAuthService:
    """Test cases for AuthService."""

    def test_validate_user_credentials_success(self, app, regular_user):
        """Test successful user credential validation."""
        with app.app_context():
            user = AuthService.validate_user_credentials('user@test.com', 'user123')
            assert user is not None
            assert user.email == 'user@test.com'

    def test_validate_user_credentials_wrong_password(self, app, regular_user):
        """Test user credential validation with wrong password."""
        with app.app_context():
            user = AuthService.validate_user_credentials('user@test.com', 'wrongpassword')
            assert user is None

    def test_validate_user_credentials_nonexistent_user(self, app):
        """Test user credential validation with nonexistent user."""
        with app.app_context():
            user = AuthService.validate_user_credentials('nonexistent@test.com', 'password')
            assert user is None

    def test_create_user_success(self, app):
        """Test successful user creation."""
        with app.app_context():
            user, error = AuthService.create_user(
                name='New User',
                email='new@test.com',
                password='newpass123'
            )

            assert user is not None
            assert error is None
            assert user.name == 'New User'
            assert user.email == 'new@test.com'
            assert user.role == 'user'
            assert check_password_hash(user.password_hash, 'newpass123')

    def test_create_user_duplicate_email(self, app, regular_user):
        """Test user creation with duplicate email."""
        with app.app_context():
            user, error = AuthService.create_user(
                name='Duplicate User',
                email='user@test.com',  # Email already exists
                password='password123'
            )

            assert user is None
            assert error == "El email ya está registrado"

    def test_create_admin_user(self, app):
        """Test admin user creation."""
        with app.app_context():
            user, error = AuthService.create_user(
                name='Admin User',
                email='admin@test.com',
                password='adminpass123',
                role='admin'
            )

            assert user is not None
            assert error is None
            assert user.role == 'admin'

    def test_update_user_profile_success(self, app, regular_user):
        """Test successful user profile update."""
        with app.app_context():
            success, message = AuthService.update_user_profile(
                user=regular_user,
                name='Updated Name',
                email='updated@test.com'
            )

            assert success is True
            assert message == "Perfil actualizado exitosamente"
            assert regular_user.name == 'Updated Name'
            assert regular_user.email == 'updated@test.com'

    def test_update_user_profile_duplicate_email(self, app, regular_user, second_user):
        """Test user profile update with duplicate email."""
        with app.app_context():
            success, message = AuthService.update_user_profile(
                user=regular_user,
                name='Updated Name',
                email='user2@test.com'  # Email belongs to second_user
            )

            assert success is False
            assert message == "El email ya está en uso por otro usuario"

    def test_update_user_profile_same_email(self, app, regular_user):
        """Test user profile update with same email (should work)."""
        with app.app_context():
            success, message = AuthService.update_user_profile(
                user=regular_user,
                name='Updated Name',
                email='user@test.com'  # Same email
            )

            assert success is True
            assert message == "Perfil actualizado exitosamente"

    def test_change_password_success(self, app, regular_user):
        """Test successful password change."""
        with app.app_context():
            success, message = AuthService.change_password(
                user=regular_user,
                current_password='user123',
                new_password='newpassword123'
            )

            assert success is True
            assert message == "Contraseña cambiada exitosamente"
            assert check_password_hash(regular_user.password_hash, 'newpassword123')

    def test_change_password_wrong_current(self, app, regular_user):
        """Test password change with wrong current password."""
        with app.app_context():
            success, message = AuthService.change_password(
                user=regular_user,
                current_password='wrongpassword',
                new_password='newpassword123'
            )

            assert success is False
            assert message == "La contraseña actual es incorrecta"

    def test_validate_password_strength_valid(self, app):
        """Test password strength validation with valid password."""
        with app.app_context():
            is_valid, message = AuthService.validate_password_strength('validpass123')

            assert is_valid is True
            assert message == "Contraseña válida"

    def test_validate_password_strength_too_short(self, app):
        """Test password strength validation with short password."""
        with app.app_context():
            is_valid, message = AuthService.validate_password_strength('123')

            assert is_valid is False
            assert message == "La contraseña debe tener al menos 6 caracteres"

    def test_validate_password_strength_minimum_length(self, app):
        """Test password strength validation with minimum length."""
        with app.app_context():
            is_valid, message = AuthService.validate_password_strength('123456')

            assert is_valid is True
            assert message == "Contraseña válida"