import os
from pathlib import Path
from flask import Flask

from .baseconfig import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Configurations specific to production. Mostly inherits from\n
    baseconfig.
    """

    # Flask
    TESTING = False
    DEBUG = False

    # Security
    SESSION_COOKIE_SAMESITE = "Strict"

    