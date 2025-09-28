from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from app import db

class AuthService:
    @staticmethod
    def validate_user_credentials(email, password):
        """Valida las credenciales del usuario"""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def create_user(name, email, password, role='user'):
        """Crea un nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "El email ya está registrado"

        # Crear nuevo usuario
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Error al crear usuario: {str(e)}"

    @staticmethod
    def update_user_profile(user, name, email):
        """Actualiza el perfil del usuario"""
        # Verificar si el nuevo email ya existe (pero no es el mismo usuario)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            return False, "El email ya está en uso por otro usuario"

        try:
            user.name = name
            user.email = email
            db.session.commit()
            return True, "Perfil actualizado exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar perfil: {str(e)}"

    @staticmethod
    def change_password(user, current_password, new_password):
        """Cambia la contraseña del usuario"""
        # Verificar contraseña actual
        if not check_password_hash(user.password_hash, current_password):
            return False, "La contraseña actual es incorrecta"

        try:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            return True, "Contraseña cambiada exitosamente"
        except Exception as e:
            db.session.rollback()
            return False, f"Error al cambiar contraseña: {str(e)}"

    @staticmethod
    def validate_password_strength(password):
        """Valida la fortaleza de la contraseña"""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"

        # Aquí se pueden agregar más validaciones
        # has_upper = any(c.isupper() for c in password)
        # has_lower = any(c.islower() for c in password)
        # has_digit = any(c.isdigit() for c in password)

        return True, "Contraseña válida"