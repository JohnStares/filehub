import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

import os


def initialize_extensions(app):
    pass


def configure_path(app):
    pass

def register_blueprints(app):
    pass


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

