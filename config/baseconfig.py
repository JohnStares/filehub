import os
from dotenv import load_dotenv
from pathlib import Path
import redis

from flask import Flask


load_dotenv()

class BaseConfig(object):
    """This class holds all configurations that are shared among all other classes of configs"""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

    # Database
    SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    # File Uploads
    UPLOAD_EXTENSIONS={"docx", "doc", "txt", "pptx", "pdf", "odt", 'ppt'}
    MAX_CONTENT_LENGTH=25 * 1024 * 1024
    MIN_CONTENT_LENGTH=10 * 1024
    FILES_PER_PAGE=15

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


    def init_app(self, app: Flask):
        # Create Base Directory
        base_dir = Path(app.root_path).resolve().parent
        app.config["BASEDIR"] = base_dir

        # Add upload path for the files to app
        dir_path = Path("/var/www/uploaded_files")
        upload_dir = app.config["BASEDIR"] / dir_path
        app.config["UPLOAD_PATH"] = upload_dir
        
