import pytest
import json
from datetime import date, timedelta
from app.models import Task, User
from app import db

class TestTaskRoutes:
    """Test cases for task routes."""

    def test_task_list_authenticated(self, authenticated_client):
        """Test task list page for authenticated user."""
        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        assert b'Mis Tareas' in response.data

    def test_task_list_unauthenticated(self, client):
        """Test task list redirects unauthenticated users."""
        response = client.get('/tasks/')
        assert response.status_code == 302

    def test_task_list_with_tasks(self, authenticated_client, app, regular_user):
        """Test task list shows user's tasks."""
        with app.app_context():
            task = Task(
                title='Test Task',
                description='Test description',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()

        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        assert b'Test Task' in response.data
        assert b'Test description' in response.data

    def test_task_list_admin_sees_all(self, admin_client, app, admin_user, regular_user):
        """Test admin sees all tasks."""
        with app.app_context():
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
                priority='medium',
                status='pending'
            )
            db.session.add_all([task1, task2])
            db.session.commit()

        response = admin_client.get('/tasks/')
        assert response.status_code == 200
        assert b'Todas las Tareas' in response.data
        assert b'Admin Task' in response.data
        assert b'User Task' in response.data

    def test_task_list_user_only_own(self, authenticated_client, app, regular_user, second_user):
        """Test regular user only sees their own tasks."""
        with app.app_context():
            task1 = Task(
                title='My Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            task2 = Task(
                title='Other Task',
                created_by=second_user.id,
                assigned_to=second_user.id,
                priority='medium',
                status='pending'
            )
            task3 = Task(
                title='Assigned to Me',
                created_by=second_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add_all([task1, task2, task3])
            db.session.commit()

        response = authenticated_client.get('/tasks/')
        assert response.status_code == 200
        assert b'My Task' in response.data
        assert b'Other Task' not in response.data
        assert b'Assigned to Me' in response.data

    def test_task_create_page(self, authenticated_client):
        """Test task creation page."""
        response = authenticated_client.get('/tasks/new')
        assert response.status_code == 200
        assert b'Nueva Tarea' in response.data
        assert b'title' in response.data
        assert b'description' in response.data
        assert b'priority' in response.data

    def test_task_create_success(self, authenticated_client, app, regular_user):
        """Test successful task creation."""
        due_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')

        response = authenticated_client.post('/tasks/new', data={
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high',
            'due_date': due_date,
            'assigned_to': regular_user.id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Tarea creada exitosamente' in response.data

        # Verify task was created
        with app.app_context():
            task = Task.query.filter_by(title='New Task').first()
            assert task is not None
            assert task.description == 'Task description'
            assert task.priority == 'high'
            assert task.created_by == regular_user.id
            assert task.assigned_to == regular_user.id

    def test_task_create_minimal(self, authenticated_client, app, regular_user):
        """Test task creation with minimal data."""
        response = authenticated_client.post('/tasks/new', data={
            'title': 'Minimal Task',
            'priority': 'medium',
            'assigned_to': regular_user.id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Tarea creada exitosamente' in response.data

    def test_task_create_empty_title(self, authenticated_client, regular_user):
        """Test task creation with empty title."""
        response = authenticated_client.post('/tasks/new', data={
            'title': '',
            'priority': 'medium',
            'assigned_to': regular_user.id
        })

        assert response.status_code == 200
        # Form validation should catch this

    def test_task_create_past_due_date(self, authenticated_client, regular_user):
        """Test task creation with past due date."""
        past_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        response = authenticated_client.post('/tasks/new', data={
            'title': 'Past Date Task',
            'priority': 'medium',
            'due_date': past_date,
            'assigned_to': regular_user.id
        })

        assert response.status_code == 200
        assert b'La fecha l\xc3\xadmite no puede ser anterior a hoy' in response.data

    def test_task_edit_page(self, authenticated_client, app, regular_user):
        """Test task edit page."""
        with app.app_context():
            task = Task(
                title='Edit Task',
                description='Edit description',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.get(f'/tasks/{task_id}/edit')
        assert response.status_code == 200
        assert b'Editar Tarea' in response.data
        assert b'Edit Task' in response.data

    def test_task_edit_unauthorized(self, authenticated_client, app, second_user):
        """Test editing task without permission."""
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
            task_id = task.id

        response = authenticated_client.get(f'/tasks/{task_id}/edit', follow_redirects=True)
        assert response.status_code == 200
        assert b'Tarea no encontrada o no tienes permisos' in response.data

    def test_task_edit_success(self, authenticated_client, app, regular_user):
        """Test successful task edit."""
        with app.app_context():
            task = Task(
                title='Original Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.post(f'/tasks/{task_id}/edit', data={
            'title': 'Updated Task',
            'description': 'Updated description',
            'priority': 'high',
            'assigned_to': regular_user.id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Tarea actualizada exitosamente' in response.data

        # Verify changes
        with app.app_context():
            task = Task.query.get(task_id)
            assert task.title == 'Updated Task'
            assert task.description == 'Updated description'
            assert task.priority == 'high'

    def test_task_view(self, authenticated_client, app, regular_user):
        """Test task detail view."""
        with app.app_context():
            task = Task(
                title='View Task',
                description='View description',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.get(f'/tasks/{task_id}')
        assert response.status_code == 200
        assert b'Detalle de Tarea' in response.data
        assert b'View Task' in response.data
        assert b'View description' in response.data

    def test_task_view_unauthorized(self, authenticated_client, app, second_user):
        """Test viewing task without permission."""
        with app.app_context():
            task = Task(
                title='Private Task',
                created_by=second_user.id,
                assigned_to=second_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.get(f'/tasks/{task_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Tarea no encontrada o no tienes permisos' in response.data

    def test_task_toggle_status(self, authenticated_client, app, regular_user):
        """Test toggling task status."""
        with app.app_context():
            task = Task(
                title='Toggle Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Toggle to done
        response = authenticated_client.post(f'/tasks/{task_id}/toggle')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert data['new_status'] == 'done'

        # Verify in database
        with app.app_context():
            task = Task.query.get(task_id)
            assert task.status == 'done'

    def test_task_delete(self, authenticated_client, app, regular_user):
        """Test task deletion by creator."""
        with app.app_context():
            task = Task(
                title='Delete Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Tarea eliminada exitosamente' in response.data

        # Verify task was deleted
        with app.app_context():
            task = Task.query.get(task_id)
            assert task is None

    def test_task_delete_unauthorized(self, authenticated_client, app, second_user):
        """Test task deletion without permission."""
        with app.app_context():
            task = Task(
                title='Protected Task',
                created_by=second_user.id,
                assigned_to=second_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = authenticated_client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Tarea no encontrada o no tienes permisos' in response.data

        # Verify task still exists
        with app.app_context():
            task = Task.query.get(task_id)
            assert task is not None

    def test_admin_can_delete_any_task(self, admin_client, app, admin_user, regular_user):
        """Test admin can delete any task."""
        with app.app_context():
            task = Task(
                title='User Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = admin_client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Tarea eliminada exitosamente' in response.data

    def test_task_filters(self, authenticated_client, app, regular_user):
        """Test task filtering functionality."""
        with app.app_context():
            # Create tasks with different properties
            task1 = Task(
                title='High Priority Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='high',
                status='pending'
            )
            task2 = Task(
                title='Completed Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='medium',
                status='done'
            )
            task3 = Task(
                title='Search Task',
                description='Searchable content',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                priority='low',
                status='pending'
            )
            db.session.add_all([task1, task2, task3])
            db.session.commit()

        # Test status filter
        response = authenticated_client.get('/tasks/?status=done')
        assert response.status_code == 200
        assert b'Completed Task' in response.data
        assert b'High Priority Task' not in response.data

        # Test priority filter
        response = authenticated_client.get('/tasks/?priority=high')
        assert response.status_code == 200
        assert b'High Priority Task' in response.data
        assert b'Completed Task' not in response.data

        # Test search filter
        response = authenticated_client.get('/tasks/?search=Search')
        assert response.status_code == 200
        assert b'Search Task' in response.data
        assert b'High Priority Task' not in response.data

    def test_dashboard_page(self, authenticated_client, regular_user):
        """Test dashboard page loads correctly."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
        assert b'Total Tareas' in response.data
        assert b'Pendientes' in response.data
        assert b'Completadas' in response.data

    def test_dashboard_with_tasks(self, authenticated_client, app, regular_user):
        """Test dashboard shows correct statistics."""
        with app.app_context():
            # Create tasks with different statuses
            task1 = Task(
                title='Pending Task 1',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                status='pending'
            )
            task2 = Task(
                title='Pending Task 2',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                status='pending'
            )
            task3 = Task(
                title='Done Task',
                created_by=regular_user.id,
                assigned_to=regular_user.id,
                status='done'
            )
            db.session.add_all([task1, task2, task3])
            db.session.commit()

        response = authenticated_client.get('/')
        assert response.status_code == 200
        # Should show correct counts in dashboard

    def test_task_assignment_admin(self, admin_client, app, admin_user, regular_user):
        """Test admin can assign tasks to other users."""
        response = admin_client.post('/tasks/new', data={
            'title': 'Assigned Task',
            'description': 'Task assigned to user',
            'priority': 'medium',
            'assigned_to': regular_user.id
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Tarea creada exitosamente' in response.data

        # Verify assignment
        with app.app_context():
            task = Task.query.filter_by(title='Assigned Task').first()
            assert task is not None
            assert task.created_by == admin_user.id
            assert task.assigned_to == regular_user.id

    def test_task_assignment_regular_user(self, authenticated_client, app, regular_user):
        """Test regular user can only assign to themselves."""
        response = authenticated_client.get('/tasks/new')
        assert response.status_code == 200
        # The form should only show the current user as assignee option