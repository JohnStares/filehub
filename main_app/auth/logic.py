from flask_login import login_user
from flask import flash

from typing import Any

from main_app.models import User
from main_app.auth.forms import AdminRegisterForm, AdminLoginForm
from main_app.extensions import db

from main_app.auth.helper import AdminNotApproved

def process_admin_registration(form: AdminRegisterForm) -> bool:
    """
    This handles the admin registration process (adding admins to the database)
    
    :param form: The form that contains admin details to be processed
    :type form: AdminRegisterForm
    :rtype: bool
    """
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data, role="admin")
            user.hash_password(form.password1.data)

            db.session.add(user)
            db.session.commit()

            return True
        
        except Exception:
            raise
    
    return False


def process_admin_login(form: AdminLoginForm) -> bool:
    """
    This handles the the login logic of admins.
    
    :param form: Form containing data
    :type form: AdminLoginForm
    :rtype: bool
    """
    if form.validate_on_submit():
        try:
            user = form.user
            if user.is_admin != True:
                raise AdminNotApproved("You are not approved to be an Admin")

            login_user(user)

            return True
        except Exception:
            raise 

    return False