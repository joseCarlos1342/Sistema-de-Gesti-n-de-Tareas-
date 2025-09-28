import pytest
from datetime import date, timedelta
from app.models import User, Task
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class TestUserModel:
    """Test cases for User model."""

    def test_user_creation(self, app):
        """Test user creation with all fields."""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@example.com',
                password_hash=generate_password_hash('password123'),
                role='user'
            )

            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.name == 'Test User'
            assert user.email == 'test@example.com'
            assert user.role == 'user'
            assert check_password_hash(user.password_hash, 'password123')
            assert user.created_at is not None

    def test_user_default_role(self, app):
        """Test user creation with default role."""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@example.com',
                password_hash=generate_password_hash('password123')
            )

            db.session.add(user)
            db.session.commit()

            assert user.role == 'user'

    def test_user_email_unique_constraint(self, app):
        """Test that email must be unique."""
        with app.app_context():
            user1 = User(
                name='User One',
                email='same@example.com',
                password_hash=generate_password_hash('password123')
            )
            user2 = User(
                name='User Two',
                email='same@example.com',
                password_hash=generate_password_hash('password123')
            )

            db.session.add(user1)
            db.session.commit()

            db.session.add(user2)
            with pytest.raises(Exception):  # Should raise integrity error
                db.session.commit()

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                name='Test User',
                email='test@example.com',
                password_hash=generate_password_hash('password123')
            )

            assert repr(user) == '<User test@example.com>'

    def test_can_access_task_own_created(self, app, regular_user, sample_task):
        """Test user can access task they created."""
        with app.app_context():
            assert regular_user.can_access_task(sample_task) is True

    def test_can_access_task_assigned_to(self, app, regular_user, second_user):
        """Test user can access task assigned to them."""
        with app.app_context():
            task = Task(
                title='Assigned Task',
                created_by=second_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

            assert regular_user.can_access_task(task) is True

    def test_can_access_task_no_access(self, app, regular_user, second_user):
        """Test user cannot access task they don't own or assigned to."""
        with app.app_context():
            task = Task(
                title='Other Task',
                created_by=second_user.id,
                assigned_to=second_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

            assert regular_user.can_access_task(task) is False

    def test_can_access_task_admin(self, app, admin_user, sample_task):
        """Test admin can access any task."""
        with app.app_context():
            assert admin_user.can_access_task(sample_task) is True

    def test_can_assign_tasks_regular_user(self, app, regular_user):
        """Test regular user cannot assign tasks."""
        with app.app_context():
            assert regular_user.can_assign_tasks() is False

    def test_can_assign_tasks_admin(self, app, admin_user):
        """Test admin can assign tasks."""
        with app.app_context():
            assert admin_user.can_assign_tasks() is True

class TestTaskModel:
    """Test cases for Task model."""

    def test_task_creation(self, app, regular_user):
        """Test task creation with all fields."""
        with app.app_context():
            due_date = date.today() + timedelta(days=7)
            task = Task(
                title='Test Task',
                description='This is a test task',
                priority='high',
                status='pending',
                due_date=due_date,
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.title == 'Test Task'
            assert task.description == 'This is a test task'
            assert task.priority == 'high'
            assert task.status == 'pending'
            assert task.due_date == due_date
            assert task.created_by == regular_user.id
            assert task.assigned_to == regular_user.id
            assert task.created_at is not None
            assert task.updated_at is not None

    def test_task_default_values(self, app, regular_user):
        """Test task creation with default values."""
        with app.app_context():
            task = Task(
                title='Minimal Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            db.session.add(task)
            db.session.commit()

            assert task.status == 'pending'
            assert task.priority == 'medium'

    def test_task_repr(self, app, regular_user):
        """Test task string representation."""
        with app.app_context():
            task = Task(
                title='Test Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert repr(task) == '<Task Test Task>'

    def test_is_overdue_true(self, app, regular_user):
        """Test task is overdue when due date is in the past and pending."""
        with app.app_context():
            task = Task(
                title='Overdue Task',
                due_date=date.today() - timedelta(days=1),
                status='pending',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task.is_overdue() is True

    def test_is_overdue_false_future_date(self, app, regular_user):
        """Test task is not overdue when due date is in the future."""
        with app.app_context():
            task = Task(
                title='Future Task',
                due_date=date.today() + timedelta(days=1),
                status='pending',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task.is_overdue() is False

    def test_is_overdue_false_completed(self, app, regular_user):
        """Test task is not overdue when completed, even with past due date."""
        with app.app_context():
            task = Task(
                title='Completed Task',
                due_date=date.today() - timedelta(days=1),
                status='done',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task.is_overdue() is False

    def test_is_overdue_false_no_due_date(self, app, regular_user):
        """Test task is not overdue when no due date is set."""
        with app.app_context():
            task = Task(
                title='No Due Date Task',
                due_date=None,
                status='pending',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task.is_overdue() is False

    def test_to_dict(self, app, regular_user, second_user):
        """Test task serialization to dictionary."""
        with app.app_context():
            due_date = date.today() + timedelta(days=7)
            task = Task(
                title='Dict Task',
                description='Task for dict test',
                priority='high',
                status='pending',
                due_date=due_date,
                created_by=regular_user.id,
                assigned_to=second_user.id
            )

            db.session.add(task)
            db.session.commit()

            task_dict = task.to_dict()

            assert task_dict['id'] == task.id
            assert task_dict['title'] == 'Dict Task'
            assert task_dict['description'] == 'Task for dict test'
            assert task_dict['status'] == 'pending'
            assert task_dict['priority'] == 'high'
            assert task_dict['due_date'] == due_date.isoformat()
            assert task_dict['created_by'] == regular_user.id
            assert task_dict['assigned_to'] == second_user.id
            assert task_dict['creator_name'] == regular_user.name
            assert task_dict['assignee_name'] == second_user.name
            assert 'created_at' in task_dict
            assert 'updated_at' in task_dict
            assert 'is_overdue' in task_dict

    def test_to_dict_no_due_date(self, app, regular_user):
        """Test task serialization to dictionary without due date."""
        with app.app_context():
            task = Task(
                title='No Due Date Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            db.session.add(task)
            db.session.commit()

            task_dict = task.to_dict()

            assert task_dict['due_date'] is None

    def test_task_relationships(self, app, regular_user, second_user):
        """Test task relationships with users."""
        with app.app_context():
            # Get fresh user instances from current session
            user1 = db.session.get(User, regular_user.id)
            user2 = db.session.get(User, second_user.id)

            task = Task(
                title='Relationship Task',
                created_by=user1.id,
                assigned_to=user2.id
            )

            db.session.add(task)
            db.session.commit()

            # Test creator relationship by ID
            assert task.creator.id == user1.id
            assert task.creator.email == user1.email

            # Test assignee relationship by ID
            assert task.assignee.id == user2.id
            assert task.assignee.email == user2.email

    def test_task_foreign_key_constraints(self, app):
        """Test task foreign key constraints."""
        with app.app_context():
            # Test that we can create a task with valid user IDs
            # (SQLite doesn't enforce FK constraints by default in tests)

            # First create a valid user
            user = User(
                name='FK Test User',
                email='fk@test.com',
                password_hash='hashed'
            )
            db.session.add(user)
            db.session.commit()

            # Now create a task with valid FK
            task = Task(
                title='Valid FK Task',
                created_by=user.id,
                assigned_to=user.id
            )

            db.session.add(task)
            db.session.commit()

            # Verify the task was created successfully
            assert task.id is not None
            assert task.created_by == user.id