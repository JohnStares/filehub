from flask import Flask
from typing import Optional

from main_app.logging import set_logger
from config import get_config, config
from main_app.utils import initialize_sentry, initialize_extensions, register_blueprints


def create_app(config_name: Optional[str] = None):
    app = Flask(__name__)

    if config_name:
        config_obj = config[config_name]
    else:
        config_obj = get_config()
        
    config_obj().init_app(app)
    app.config.from_object(config_obj)

   # Initialize extensions
    initialize_extensions(app)
    initialize_sentry()

    # set up logging functionality
    set_logger(app=app, basedir=app.config["BASEDIR"])

    # Register handlers
    from main_app.logging import register_handlers
    register_handlers(app)

    # Register blueprints
    register_blueprints(app)

    @app.cli.command("create-db")
    def create_db():
        from main_app.extensions import db
        """Create database tables for development only"""
        print("Creating database tables...")
        db.create_all()
        print("Database tables created!")

    return app


