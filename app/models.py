from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assignee', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def can_access_task(self, task):
        """Verifica si el usuario puede acceder a una tarea específica"""
        return self.role == 'admin' or task.created_by == self.id or task.assigned_to == self.id

    def can_assign_tasks(self):
        """Verifica si el usuario puede asignar tareas a otros usuarios"""
        return self.role == 'admin'

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending' or 'done'
    priority = db.Column(db.String(20), nullable=False, default='medium')  # 'low', 'medium', 'high'
    due_date = db.Column(db.Date, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índices compuestos para optimizar consultas
    __table_args__ = (
        db.Index('idx_assigned_status', 'assigned_to', 'status'),
        db.Index('idx_due_date_status', 'due_date', 'status'),
    )

    def __repr__(self):
        return f'<Task {self.title}>'

    def is_overdue(self):
        """Verifica si la tarea está vencida"""
        if self.due_date and self.status == 'pending':
            return self.due_date < datetime.utcnow().date()
        return False

    def to_dict(self):
        """Convierte la tarea a diccionario para APIs"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'creator_name': self.creator.name if self.creator else None,
            'assignee_name': self.assignee.name if self.assignee else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_overdue': self.is_overdue()
        }