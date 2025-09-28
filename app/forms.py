from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.widgets import TextArea
from app.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirmar Contraseña',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class ProfileForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Actualizar Perfil')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nueva Contraseña',
                                   validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Cambiar Contraseña')

class TaskForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=1000)])
    priority = SelectField('Prioridad',
                          choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')],
                          default='medium')
    due_date = DateField('Fecha límite', validators=[Optional()])
    assigned_to = SelectField('Asignado a', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Tarea')

    def __init__(self, current_user, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        # Si es admin, puede asignar a cualquier usuario
        if current_user.role == 'admin':
            users = User.query.all()
            self.assigned_to.choices = [(user.id, user.name) for user in users]
        else:
            # Usuario normal solo puede asignarse a sí mismo
            self.assigned_to.choices = [(current_user.id, current_user.name)]
            self.assigned_to.data = current_user.id

class TaskFilterForm(FlaskForm):
    search = StringField('Buscar', validators=[Optional()])
    status = SelectField('Estado',
                        choices=[('', 'Todos'), ('pending', 'Pendiente'), ('done', 'Completada')],
                        default='')
    priority = SelectField('Prioridad',
                          choices=[('', 'Todas'), ('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')],
                          default='')
    assigned_to = SelectField('Asignado a',
                             coerce=lambda x: int(x) if x and (isinstance(x, int) or (isinstance(x, str) and x.isdigit())) else None,
                             validators=[Optional()])
    submit = SubmitField('Filtrar')

    def __init__(self, current_user, *args, **kwargs):
        super(TaskFilterForm, self).__init__(*args, **kwargs)

        # Configurar opciones de asignado según el rol del usuario
        if current_user.role == 'admin':
            users = User.query.all()
            self.assigned_to.choices = [(None, 'Todos')] + [(user.id, user.name) for user in users]
        else:
            # Usuario normal solo ve sus tareas
            self.assigned_to.choices = [(None, 'Mis tareas'), (current_user.id, current_user.name)]