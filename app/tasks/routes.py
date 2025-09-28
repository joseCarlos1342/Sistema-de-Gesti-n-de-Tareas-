from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app.forms import TaskForm, TaskFilterForm
from app.services.task_service import TaskService
from app.models import User, Task
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

def require_login():
    """Decorator para requerir autenticación"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página.', 'error')
        return redirect(url_for('auth.login'))
    return None

@tasks_bp.before_request
def before_request():
    """Verificar autenticación antes de cada request"""
    redirect_response = require_login()
    if redirect_response:
        return redirect_response

@tasks_bp.route('/')
def list_tasks():
    user = User.query.get(session['user_id'])
    filter_form = TaskFilterForm(current_user=user)

    # Obtener filtros de la URL
    filters = {}
    if request.args.get('search'):
        filters['search'] = request.args.get('search')
        filter_form.search.data = filters['search']

    if request.args.get('status'):
        filters['status'] = request.args.get('status')
        filter_form.status.data = filters['status']

    if request.args.get('priority'):
        filters['priority'] = request.args.get('priority')
        filter_form.priority.data = filters['priority']

    assigned_to_param = request.args.get('assigned_to')
    if assigned_to_param and assigned_to_param.isdigit():
        try:
            filters['assigned_to'] = int(assigned_to_param)
            filter_form.assigned_to.data = filters['assigned_to']
        except (ValueError, TypeError):
            pass

    # Obtener tareas con filtros
    tasks = TaskService.get_user_tasks(user, filters)

    return render_template('tasks/list.html', tasks=tasks, filter_form=filter_form, user=user)

@tasks_bp.route('/new', methods=['GET', 'POST'])
def create_task():
    user = User.query.get(session['user_id'])
    form = TaskForm(current_user=user)

    if form.validate_on_submit():
        # Validar datos
        is_valid, errors = TaskService.validate_task_data(
            title=form.title.data,
            due_date=form.due_date.data
        )

        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('tasks/form.html', form=form, title='Nueva Tarea')

        # Crear tarea
        task, error = TaskService.create_task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            created_by=user.id,
            assigned_to=form.assigned_to.data
        )

        if task:
            flash('Tarea creada exitosamente.', 'success')
            return redirect(url_for('tasks.list_tasks'))
        else:
            flash(error, 'error')

    return render_template('tasks/form.html', form=form, title='Nueva Tarea')

@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    user = User.query.get(session['user_id'])
    task = TaskService.get_task_by_id(task_id, user)

    if not task:
        flash('Tarea no encontrada o no tienes permisos para editarla.', 'error')
        return redirect(url_for('tasks.list_tasks'))

    form = TaskForm(current_user=user, obj=task)

    if form.validate_on_submit():
        # Validar datos
        is_valid, errors = TaskService.validate_task_data(
            title=form.title.data,
            due_date=form.due_date.data
        )

        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('tasks/form.html', form=form, title='Editar Tarea', task=task)

        # Actualizar tarea
        assigned_to = form.assigned_to.data if user.can_assign_tasks() else None
        success, message = TaskService.update_task(
            task=task,
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            assigned_to=assigned_to
        )

        if success:
            flash(message, 'success')
            return redirect(url_for('tasks.list_tasks'))
        else:
            flash(message, 'error')

    return render_template('tasks/form.html', form=form, title='Editar Tarea', task=task)

@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    user = User.query.get(session['user_id'])
    task = TaskService.get_task_by_id(task_id, user)

    if not task:
        flash('Tarea no encontrada o no tienes permisos para eliminarla.', 'error')
        return redirect(url_for('tasks.list_tasks'))

    # Solo el creador o admin pueden eliminar
    if task.created_by != user.id and user.role != 'admin':
        flash('No tienes permisos para eliminar esta tarea.', 'error')
        return redirect(url_for('tasks.list_tasks'))

    success, message = TaskService.delete_task(task)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    user = User.query.get(session['user_id'])
    task = TaskService.get_task_by_id(task_id, user)

    if not task:
        return jsonify({'success': False, 'message': 'Tarea no encontrada'}), 404

    success, message = TaskService.toggle_task_status(task)

    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': success,
            'message': message,
            'new_status': task.status if success else None
        })

    flash(message, 'success' if success else 'error')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/<int:task_id>')
def view_task(task_id):
    user = User.query.get(session['user_id'])
    task = TaskService.get_task_by_id(task_id, user)

    if not task:
        flash('Tarea no encontrada o no tienes permisos para verla.', 'error')
        return redirect(url_for('tasks.list_tasks'))

    return render_template('tasks/detail.html', task=task, user=user)