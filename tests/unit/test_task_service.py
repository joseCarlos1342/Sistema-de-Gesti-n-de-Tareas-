import pytest
from datetime import date, datetime, timedelta
from app.services.task_service import TaskService
from app.models import Task, User
from app import db

class TestTaskService:
    """Test cases for TaskService."""

    def test_create_task_success(self, app, regular_user):
        """Test successful task creation."""
        with app.app_context():
            task, error = TaskService.create_task(
                title='New Task',
                description='Task description',
                priority='high',
                due_date=date.today() + timedelta(days=7),
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task is not None
            assert error is None
            assert task.title == 'New Task'
            assert task.description == 'Task description'
            assert task.priority == 'high'
            assert task.status == 'pending'
            assert task.created_by == regular_user.id
            assert task.assigned_to == regular_user.id

    def test_create_task_minimal_data(self, app, regular_user):
        """Test task creation with minimal required data."""
        with app.app_context():
            task, error = TaskService.create_task(
                title='Minimal Task',
                description=None,
                priority='medium',
                due_date=None,
                created_by=regular_user.id,
                assigned_to=regular_user.id
            )

            assert task is not None
            assert error is None
            assert task.title == 'Minimal Task'
            assert task.description is None
            assert task.due_date is None

    def test_update_task_success(self, app, sample_task):
        """Test successful task update."""
        with app.app_context():
            success, message = TaskService.update_task(
                task=sample_task,
                title='Updated Task',
                description='Updated description',
                priority='high',
                due_date=date.today() + timedelta(days=14)
            )

            assert success is True
            assert message == "Tarea actualizada exitosamente"
            assert sample_task.title == 'Updated Task'
            assert sample_task.description == 'Updated description'
            assert sample_task.priority == 'high'

    def test_update_task_with_assignment(self, app, sample_task, second_user):
        """Test task update with assignment change."""
        with app.app_context():
            success, message = TaskService.update_task(
                task=sample_task,
                title='Updated Task',
                description='Updated description',
                priority='high',
                due_date=date.today() + timedelta(days=14),
                assigned_to=second_user.id
            )

            assert success is True
            assert sample_task.assigned_to == second_user.id

    def test_toggle_task_status_to_done(self, app, sample_task):
        """Test toggling task status from pending to done."""
        with app.app_context():
            assert sample_task.status == 'pending'

            success, message = TaskService.toggle_task_status(sample_task)

            assert success is True
            assert message == "Tarea marcada como done"
            assert sample_task.status == 'done'

    def test_toggle_task_status_to_pending(self, app, sample_task):
        """Test toggling task status from done to pending."""
        with app.app_context():
            # First set to done
            sample_task.status = 'done'
            db.session.commit()

            success, message = TaskService.toggle_task_status(sample_task)

            assert success is True
            assert message == "Tarea marcada como pending"
            assert sample_task.status == 'pending'

    def test_delete_task_success(self, app, sample_task):
        """Test successful task deletion."""
        with app.app_context():
            task_id = sample_task.id
            # Get fresh task instance from current session
            task = db.session.get(Task, task_id)

            success, message = TaskService.delete_task(task)

            assert success is True
            assert message == "Tarea eliminada exitosamente"
            assert db.session.get(Task, task_id) is None

    def test_get_user_tasks_regular_user(self, app, regular_user, second_user):
        """Test getting tasks for regular user (only their tasks)."""
        with app.app_context():
            # Create tasks for both users
            task1 = Task(
                title='User 1 Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            task2 = Task(
                title='User 2 Task',
                created_by=second_user.id,
                assigned_to=second_user.id,
                priority='high',
                status='pending'
            )
            task3 = Task(
                title='Assigned to User 1',
                created_by=second_user.id,
                assigned_to=regular_user.id,
                priority='low',
                status='pending'
            )

            db.session.add_all([task1, task2, task3])
            db.session.commit()

            tasks = TaskService.get_user_tasks(regular_user)

            # Should get task1 (created by) and task3 (assigned to)
            assert len(tasks) == 2
            task_titles = [task.title for task in tasks]
            assert 'User 1 Task' in task_titles
            assert 'Assigned to User 1' in task_titles
            assert 'User 2 Task' not in task_titles

    def test_get_user_tasks_admin(self, app, admin_user, regular_user):
        """Test getting tasks for admin user (all tasks)."""
        with app.app_context():
            # Create tasks
            task1 = Task(
                title='Admin Task',
                created_by=admin_user.id,
                assigned_to=admin_user.id,
                priority='medium',
                status='pending'
            )
            task2 = Task(
                title='User Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='high',
                status='pending'
            )

            db.session.add_all([task1, task2])
            db.session.commit()

            tasks = TaskService.get_user_tasks(admin_user)

            # Admin should see all tasks
            assert len(tasks) == 2

    def test_get_user_tasks_with_filters(self, app, regular_user):
        """Test getting user tasks with filters."""
        with app.app_context():
            # Create tasks with different properties
            task1 = Task(
                title='High Priority Task',
                description='Important task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='high',
                status='pending'
            )
            task2 = Task(
                title='Low Priority Task',
                description='Less important',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='low',
                status='done'
            )
            task3 = Task(
                title='Search Test Task',
                description='Searchable content',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )

            db.session.add_all([task1, task2, task3])
            db.session.commit()

            # Test status filter
            pending_tasks = TaskService.get_user_tasks(regular_user, {'status': 'pending'})
            assert len(pending_tasks) == 2

            # Test priority filter
            high_tasks = TaskService.get_user_tasks(regular_user, {'priority': 'high'})
            assert len(high_tasks) == 1
            assert high_tasks[0].title == 'High Priority Task'

            # Test search filter
            search_tasks = TaskService.get_user_tasks(regular_user, {'search': 'Search'})
            assert len(search_tasks) == 1
            assert search_tasks[0].title == 'Search Test Task'

    def test_get_task_by_id_authorized(self, app, regular_user, sample_task):
        """Test getting task by ID with proper authorization."""
        with app.app_context():
            task = TaskService.get_task_by_id(sample_task.id, regular_user)
            assert task is not None
            assert task.id == sample_task.id

    def test_get_task_by_id_unauthorized(self, app, second_user, sample_task):
        """Test getting task by ID without authorization."""
        with app.app_context():
            task = TaskService.get_task_by_id(sample_task.id, second_user)
            assert task is None

    def test_get_task_by_id_admin_access(self, app, admin_user, sample_task):
        """Test admin can access any task."""
        with app.app_context():
            task = TaskService.get_task_by_id(sample_task.id, admin_user)
            assert task is not None
            assert task.id == sample_task.id

    def test_get_task_statistics(self, app, regular_user):
        """Test getting task statistics."""
        with app.app_context():
            # Create tasks with different statuses
            task1 = Task(
                title='Pending Task 1',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending',
                due_date=date.today() - timedelta(days=1)  # Overdue
            )
            task2 = Task(
                title='Pending Task 2',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            task3 = Task(
                title='Done Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='done'
            )

            db.session.add_all([task1, task2, task3])
            db.session.commit()

            stats = TaskService.get_task_statistics(regular_user)

            assert stats['total'] == 3
            assert stats['pending'] == 2
            assert stats['completed'] == 1
            assert stats['overdue'] == 1

    def test_validate_task_data_valid(self, app):
        """Test task data validation with valid data."""
        with app.app_context():
            is_valid, errors = TaskService.validate_task_data(
                title='Valid Task',
                due_date=date.today() + timedelta(days=1)
            )

            assert is_valid is True
            assert errors == []

    def test_validate_task_data_empty_title(self, app):
        """Test task data validation with empty title."""
        with app.app_context():
            is_valid, errors = TaskService.validate_task_data(
                title='',
                due_date=date.today() + timedelta(days=1)
            )

            assert is_valid is False
            assert "El título es obligatorio" in errors

    def test_validate_task_data_long_title(self, app):
        """Test task data validation with overly long title."""
        with app.app_context():
            long_title = 'x' * 201  # Longer than 200 characters

            is_valid, errors = TaskService.validate_task_data(
                title=long_title,
                due_date=date.today() + timedelta(days=1)
            )

            assert is_valid is False
            assert "El título no puede exceder 200 caracteres" in errors

    def test_validate_task_data_past_due_date(self, app):
        """Test task data validation with past due date."""
        with app.app_context():
            is_valid, errors = TaskService.validate_task_data(
                title='Valid Task',
                due_date=date.today() - timedelta(days=1)
            )

            assert is_valid is False
            assert "La fecha límite no puede ser anterior a hoy" in errors

    def test_validate_task_data_no_due_date(self, app):
        """Test task data validation without due date."""
        with app.app_context():
            is_valid, errors = TaskService.validate_task_data(
                title='Valid Task',
                due_date=None
            )

            assert is_valid is True
            assert errors == []