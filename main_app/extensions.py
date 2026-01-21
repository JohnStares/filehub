from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_wtf import CSRFProtect
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_talisman import Talisman
import redis

import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
talisman = Talisman()

def get_redis_url() -> tuple[str, redis.Redis]:
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    redis_password = os.environ.get("REDIS_PASSWORD")
    redis_db = os.environ.get("REDIS_DB", 0)
    redis_username = os.environ.get("REDIS_USERNAME")

    redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    if isinstance(redis_host, str) and ":" in redis_host :
        parts = redis_host.split(":")
        redis_host = parts[0]

    redis_port = int(str(redis_port))

    # Get redis connection
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=redis_db,
        username=redis_username,
        socket_timeout=5,
        decode_responses=True,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        max_connections=20

    )

    # Ping Redis
    try:
        redis_client.ping()
        print("Pinged redis successfully")
    except redis.ConnectionError as e:
        print(f"Couldn't ping redis due to {str(e)}")
        raise 

    return redis_url, redis_client


redis_url, redis_client = get_redis_url()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_url, #"redis://localhost:6379",
    storage_options={
        "connection_pool": redis_client.connection_pool
    } 
)