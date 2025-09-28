from flask import Blueprint, render_template, redirect, url_for, session
from app.models import User
from app.services.task_service import TaskService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Obtener estadísticas del dashboard
    stats = TaskService.get_task_statistics(user)

    # Obtener tareas recientes
    recent_tasks = TaskService.get_user_tasks(user)[:5]

    return render_template('dashboard.html', user=user, stats=stats, recent_tasks=recent_tasks)

@main_bp.route('/dashboard')
def dashboard():
    return redirect(url_for('main.index'))