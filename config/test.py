import os

from flask import Flask
from pathlib import Path

from .baseconfig import BaseConfig

class TestingConfig(BaseConfig):
    """
    Testing configurations
    """

    # Flask
    TESTING = True
    DEBUG = False

    # Database
    SQLALCHEMY_DATABASE_URI=f"sqlite:///test.db"

    # Security
    SECRET_KEY = "Teesting coniaihfgerfsehgviudgvhirtgsegfter"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED=False


    def init_app(self, app: Flask):
        # Create Base Directory
        base_dir = Path(app.root_path).resolve().parent
        app.config["HOME_DIR"] = base_dir

        # Add upload path for the files to app
        dir_path = "uploaded_test_files"
        upload_dir = app.config["HOME_DIR"] / dir_path
        app.config["UPLOAD_PATH"] = upload_dir
        