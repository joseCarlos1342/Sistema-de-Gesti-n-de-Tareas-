import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Task
from werkzeug.security import generate_password_hash
from datetime import datetime, date

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(testing=True)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            name='Admin Test',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Ensure user is bound to session
        yield user

@pytest.fixture
def regular_user(app):
    """Create a regular user for testing."""
    with app.app_context():
        user = User(
            name='User Test',
            email='user@test.com',
            password_hash=generate_password_hash('user123'),
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Ensure user is bound to session
        yield user

@pytest.fixture
def second_user(app):
    """Create a second regular user for testing."""
    with app.app_context():
        user = User(
            name='User Two',
            email='user2@test.com',
            password_hash=generate_password_hash('user123'),
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)  # Ensure user is bound to session
        yield user

@pytest.fixture
def sample_task(app, regular_user):
    """Create a sample task for testing."""
    with app.app_context():
        # Get fresh user instance from current session
        user = db.session.get(User, regular_user.id)
        task = Task(
            title='Test Task',
            description='This is a test task',
            priority='medium',
            status='pending',
            due_date=date(2024, 12, 31),
            created_by=user.id,
            assigned_to=user.id
        )
        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)  # Ensure task is bound to session
        yield task

@pytest.fixture
def authenticated_client(client, regular_user):
    """A client with an authenticated regular user."""
    with client.session_transaction() as sess:
        sess['user_id'] = regular_user.id
        sess['user_name'] = regular_user.name
        sess['user_role'] = regular_user.role
    return client

@pytest.fixture
def admin_client(client, admin_user):
    """A client with an authenticated admin user."""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['user_name'] = admin_user.name
        sess['user_role'] = admin_user.role
    return client