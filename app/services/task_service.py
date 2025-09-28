from datetime import datetime, date
from sqlalchemy import and_, or_
from app.models import Task, User
from app import db

class TaskService:
    @staticmethod
    def create_task(title, description, priority, due_date, created_by, assigned_to):
        """Crea una nueva tarea"""
        try:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                created_by=created_by,
                assigned_to=assigned_to,
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            return task, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error al crear tarea: {str(e)}"

    @staticmethod
    def update_task(task, title, description, priority, due_date, assigned_to=None):
        """Actualiza una tarea existente"""
        try:
            task.title = title
            task.description = description
            task.priority = priority
            task.due_date = due_date
            if assigned_to is not None:
                task.assigned_to = assigned_to
            task.updated_at = datetime.utcnow()
            db.session.commit()
            return True, "Tarea actualizada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar tarea: {str(e)}"

    @staticmethod
    def toggle_task_status(task):
        """Cambia el estado de una tarea entre pendiente y completada"""
        try:
            task.status = 'done' if task.status == 'pending' else 'pending'
            task.updated_at = datetime.utcnow()
            db.session.commit()
            return True, f"Tarea marcada como {task.status}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al cambiar estado: {str(e)}"

    @staticmethod
    def delete_task(task):
        """Elimina una tarea"""
        try:
            db.session.delete(task)
            db.session.commit()
            return True, "Tarea eliminada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar tarea: {str(e)}"

    @staticmethod
    def get_user_tasks(user, filters=None):
        """Obtiene las tareas de un usuario con filtros opcionales"""
        query = Task.query

        # Filtrar por autorización
        if user.role != 'admin':
            query = query.filter(
                or_(Task.created_by == user.id, Task.assigned_to == user.id)
            )

        # Aplicar filtros adicionales
        if filters:
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Task.title.ilike(search_term),
                        Task.description.ilike(search_term)
                    )
                )

            if filters.get('status'):
                query = query.filter(Task.status == filters['status'])

            if filters.get('priority'):
                query = query.filter(Task.priority == filters['priority'])

            if filters.get('assigned_to'):
                query = query.filter(Task.assigned_to == filters['assigned_to'])

            if filters.get('due_from'):
                query = query.filter(Task.due_date >= filters['due_from'])

            if filters.get('due_to'):
                query = query.filter(Task.due_date <= filters['due_to'])

        return query.order_by(Task.created_at.desc()).all()

    @staticmethod
    def get_task_by_id(task_id, user):
        """Obtiene una tarea por ID verificando permisos"""
        task = Task.query.get_or_404(task_id)

        # Verificar autorización
        if not user.can_access_task(task):
            return None

        return task

    @staticmethod
    def get_task_statistics(user):
        """Obtiene estadísticas de tareas para un usuario"""
        base_query = Task.query

        if user.role != 'admin':
            base_query = base_query.filter(
                or_(Task.created_by == user.id, Task.assigned_to == user.id)
            )

        total_tasks = base_query.count()
        pending_tasks = base_query.filter(Task.status == 'pending').count()
        completed_tasks = base_query.filter(Task.status == 'done').count()

        # Tareas vencidas
        overdue_tasks = base_query.filter(
            and_(
                Task.status == 'pending',
                Task.due_date < date.today()
            )
        ).count()

        return {
            'total': total_tasks,
            'pending': pending_tasks,
            'completed': completed_tasks,
            'overdue': overdue_tasks
        }

    @staticmethod
    def validate_task_data(title, due_date=None):
        """Valida los datos de una tarea"""
        errors = []

        if not title or len(title.strip()) == 0:
            errors.append("El título es obligatorio")

        if title and len(title) > 200:
            errors.append("El título no puede exceder 200 caracteres")

        if due_date and due_date < date.today():
            errors.append("La fecha límite no puede ser anterior a hoy")

        return len(errors) == 0, errors