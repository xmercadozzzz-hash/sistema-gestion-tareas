# app/__init__.py
import os
from flask import Flask
from app.extensions import db, login_manager, csrf
from config import Config

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import models

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    from app.routes.auth_routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.task_routes import bp as task_bp
    app.register_blueprint(task_bp)

    return app