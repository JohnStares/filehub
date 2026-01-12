from flask import Flask
from typing import Optional

from main_app.logging import set_logger
from config import get_config, config


def create_app(config_name: Optional[str] = None):
    app = Flask(__name__)

    if config_name:
        config_obj = config[config_name]
        config_obj().init_app(app)
        app.config.from_object(config_obj)
    else:
        config_obj = get_config()
        config_obj().init_app(app)
        app.config.from_object(config_obj)
   
   # Initialize extensions
    from .extensions import (db, migrate, login_manager, limiter, csrf, mail)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    limiter.init_app(app)

    csrf.init_app(app)
    mail.init_app(app)

    # set up logging functionality
    set_logger(app=app, basedir=app.config["BASEDIR"])

    # Register handlers
    from main_app.logging import register_handlers
    register_handlers(app)

    # Register blueprints
    from main_app.auth import auth_bp
    from main_app.main import main_bp
    from main_app.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.cli.command("create-db")
    def create_db():
        """Create database tables for development only"""
        print("Creating database tables...")
        db.create_all()
        print("Database tables created!")

    return app


