from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config, TestConfig
import os
from datetime import datetime

db = SQLAlchemy()

def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    db.init_app(app)

    from app.auth.routes import auth_bp
    from app.tasks.routes import tasks_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    from app.main_routes import main_bp
    app.register_blueprint(main_bp)

    # Agregar función now al contexto de Jinja2
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    with app.app_context():
        if not os.path.exists('instance'):
            os.makedirs('instance')
        db.create_all()

        # Crear usuario admin por defecto si no existe
        from app.models import User
        from werkzeug.security import generate_password_hash

        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                name='Administrator',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

    return app