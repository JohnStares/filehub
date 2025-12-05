import os

from .baseconfig import BaseConfig
from .dev import DevelopmentConfig
from .prod import ProductionConfig
from .test import TestingConfig


# Map config to their respective classes
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

def get_config():
    """Factory function to get config base on FLASK_ENV"""
    env = os.environ.get("FLASK_ENV", "default")

    return config.get(env, "default")