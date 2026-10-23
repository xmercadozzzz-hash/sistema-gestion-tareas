import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    # Acepta una clase de configuración o un diccionario para las pruebas.
    if isinstance(config_class, dict):
        app.config.from_object(Config)
        app.config.update(config_class)
    else:
        app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    # Comparte una sola instancia de cada extensión en toda la aplicación.
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    from app.routes.auth_routes import bp as auth_bp
    from app.routes.task_routes import bp as task_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app
