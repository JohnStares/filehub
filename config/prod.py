import os
from pathlib import Path
from typing import Union, Tuple

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

    # Mail Setup
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_DEFAULT_SENDER:  Union[Tuple[str, str], None] = None

    