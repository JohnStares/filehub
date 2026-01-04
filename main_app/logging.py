import logging
from logging.handlers import RotatingFileHandler
from flask import request, render_template
from flask_limiter.errors import RateLimitExceeded

def set_logger(app, basedir):
    """
    This function sets up logging and its neccesities that the app needs to log a log.

    :param:
        app: The name of your app\n
        basedir: The root directory of the application
    """

    # Create a directory if it doesn't exist
    log_directory = basedir / "logs"

    try:
        if not log_directory.exists():
            log_directory.mkdir(parents=True, exist_ok=True)

    except Exception as e:
        raise Exception

    if app.debug:

        # Set logger for console
        console_hander = logging.StreamHandler()

        console_hander.setFormatter(
            logging.Formatter(
                "%(asctime)s: %(levelname)s:: %(message)s [in %(pathname)s:%(lineno)d]",
                style="%",
                datefmt="%Y-%m-%d %H:%M"
            )
        )

        console_hander.setLevel(logging.DEBUG)

        app.logger.addHandler(console_hander)

    else:
        # Set up logger for file
        file_handler =  RotatingFileHandler(
            str(log_directory / "app.log"),
            mode="a",
            maxBytes=20240000, # 20MB
            backupCount=2 # Two backup files
        )

        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s: %(levelname)s:: %(message)s [in %(pathname)s:%(lineno)d]",
                style="%",
                datefmt="%Y-%m-%d %H:%M"
            )
        )

        # Set minimal log for the file note: Debug logs won't be recorded
        file_handler.setLevel(logging.INFO)

        # Add the handler to the application
        app.logger.addHandler(file_handler)


        # Another file logger only for errors
        error_logger = RotatingFileHandler(
            str(log_directory / "error.log"),
            mode="a",
            maxBytes=20240000,
            backupCount=2
        )

        error_logger.setFormatter(
            logging.Formatter(
                "%(asctime)s: %(levelname)s:: %(message)s [in %(pathname)s:%(lineno)d in %(funcName)s]",
                style="%",
                datefmt="%Y-%m-%d %H:%M"
            )
        )

        # Set minimal log for the file note: Debug logd won't be recorded
        error_logger.setLevel(logging.ERROR)

        # Add the handler to the application
        app.logger.addHandler(error_logger)


def register_handlers(app):
    @app.before_request
    def log_request_info():
        """This logs a request before it is being handled"""
        app.logger.info(
            f"Request: {request.method}:{request.path} from {request.remote_addr}"
        )

    @app.after_request
    def log_response_info(response):
        """This logs a handled request known as respoonse"""
        app.logger.info(
            f"Response: {response.status_code} for {request.method}:{request.path}"
        )

        return response


    @app.errorhandler(404)
    def not_found(error):
        """This logs all not found errors"""
        app.logger.info(f"404 error: {request.path} from {request.remote_addr}")

        return "404 Not Found", 404


    @app.errorhandler(500)
    def internal_server_error(error):
        """This handles all internal server error"""
        app.logger.error(f"Internal server error: {error} from {request.path}", exc_info=True)

        return render_template("errors/500.html")



    @app.errorhandler(Exception)
    def unexpected_error(error):
        """This handles all unhandles exceptions"""
        app.logger.exception(f"Unexpected error: {error} from {request.path}", exc_info=True)

        return "An error occured", 500
    
    
    @app.errorhandler(RateLimitExceeded)
    def too_many_request(error):
        """This handles 429 status_code"""
        app.logger.error(f"Too many request: {error} from {request.path}", exc_info=True)

        return render_template("errors/429.html", error=error)