from functools import wraps
from flask_login import current_user
from flask import abort


def admin_required(func):
    """
    Ensures that a user is logged in, authenticated and an admin.
    
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ["admin", "super_admin"]:
            abort(403)
            
        return func(*args, **kwargs)
    
    return wrapper