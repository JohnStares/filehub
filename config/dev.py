import os

from flask import Flask
from pathlib import Path

from .baseconfig import BaseConfig

class DevelopmentConfig(BaseConfig):
    """
    Configuration strictly for development. Inherits most configs from baseconfig but changes\n
    specific things neccessary for development
    """

    # Flask
    TESTING = False
    DEBUG = True

    # Database
    SQLALCHEMY_DATABASE_URI=f"sqlite:///filesharing.db"

    # Security
    SESSION_COOKIE_SECURE = False

    # Debug Toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Development Tools
    FLASK_RUN_EXTRA_FILES = ['config/dev.py']

    def init_app(self, app: Flask):
        # Create Base Directory
        base_dir = Path(app.root_path).resolve().parent
        app.config["BASEDIR"] = base_dir

        # Add upload path for the files to app
        dir_path = "uploaded_files"
        upload_dir = app.config["BASEDIR"] / dir_path
        app.config["UPLOAD_PATH"] = upload_dir
        