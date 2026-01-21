import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import os

from main_app.extensions import (db, migrate, login_manager, limiter, csrf, mail, talisman)
from main_app.auth import auth_bp
from main_app.main import main_bp
from main_app.admin import admin_bp

def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    limiter.init_app(app)

    csrf.init_app(app)
    mail.init_app(app)
    talisman.init_app(
        app,

        # Force hsts in production
        force_https=True if not app.debug or not app.testing else False,
        force_https_permanent=True if not app.debug or not app.testing else False,

        strict_transport_security_max_age=31536000 if not app.debug or not app.testing else 300,

        feature_policy={
            'geolocation': "'none'",
            'camera': "'none'",
            'microphone': "'none'",
        },
    )


def configure_path(app):
    pass

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")


def initialize_sentry():
    """
    This fuction initializes sentry sdk for app monitoring and error notification
    """
    sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DNS"),

    # Environment
    environment="development",

    # Performance Monitoring
    traces_sample_rate=0.1,
    profiles_sample_rate=0.01,

    # Error Handling
    sample_rate=1.0,
    attach_stacktrace=True,
    send_default_pii=False,

    # Integrations
    integrations=[
        FlaskIntegration(),
        SqlalchemyIntegration(),
        RedisIntegration()
    ],

    # Request handling
    max_request_body_size="small"
)

