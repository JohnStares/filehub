from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_wtf import CSRFProtect
from flask_limiter.util import get_remote_address
from flask_mail import Mail

import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

def get_redis_url() -> str:
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    redis_password = os.environ.get("REDIS_PASSWORD")
    redis_db = os.environ.get("REDIS_DB", 0)

    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    return redis_url

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=get_redis_url() # You can create another function where all functionalities can be called from and used.
)