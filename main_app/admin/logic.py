import sqlalchemy as sql
from flask_login import current_user
from flask import current_app

from main_app.models import User
from main_app.extensions import db
from main_app.admin.forms import RegisterUserForm, EditUser
from main_app.admin.helper import (
    get_user_by_id, get_user_by_email, get_user_by_name
)
from main_app.admin.exception import CannotDeleteAdmin, UserAlreadyExist, EmailAlreadyExist


def registered_user(form: RegisterUserForm) -> bool:
    """
    This function enables admins to create non-admin users
    
    :param form: The form filled by the admin. contains all informations to create a user
    :type form: RegisterUserForm
    :return: Returns True if the creation is successful else False
    :rtype: bool
    """
    if form.validate_on_submit():
        try:
            User.create_user(form.username.data, form.email.data, form.password1.data)

            return True
        
        except Exception:
            raise
    
    return False


def user_deleted(user_id: str) -> bool:
    """
    Docstring for user_delete
    
    :param user_id: Description
    :type user_id: int
    :return: Description
    :rtype: bool
    """
    try:
        user = get_user_by_id(int(user_id))

        if not user:
            return False
        
        if current_user.role == "admin" and user.role == "admin":
            raise CannotDeleteAdmin("Admin cannot delete admin")
        
        db.session.delete(user)
        db.session.commit()

        return True
    except Exception:
        raise



def paginate_users(page_nun: int):
    """
    Docstring for paginate_uses
    
    :param page_nun: Description
    :type page_nun: int
    """
    query = sql.select(User)
    users = db.paginate(query, page=page_nun, per_page=current_app.config["USERS_PER_PAGE"], error_out=False)

    return users



def is_user_edited(form: EditUser, user: User) -> bool:
    """
    Docstring for is_user_edited
    
    :param form: Description
    :type form: EditUser
    :return: Description
    :rtype: bool
    """
    if form.validate_on_submit():
        try:
            # This holds the value of the existing detials incase just one information is changed
            prev_username = user.username
            prev_email = user.email

            username = form.username.data
            email = form.email.data

            if prev_username != username:
                if get_user_by_name(username) is not None:
                    form.username.errors = ["Please provide another username"]
                    raise UserAlreadyExist("User with the name already exist")
            
            if prev_email != email:
                if get_user_by_email(email) is not None:
                    form.email.errors = ["Please provide another email"]
                    raise EmailAlreadyExist("User with the email already exist")
                
            user.username = username
            user.email = email

            db.session.commit()

            return True
        
        except Exception:
            raise

    return False


def is_admin_approved(admin_id: int) -> bool:
    """
    Docstring for is_admin_approved_or_revoked
    
    :param admin_id: Description
    :type admin_id: int
    :return: Description
    :rtype: bool
    """
    admin = get_user_by_id(admin_id)

    if admin:
        admin.is_admin = True
        db.session.commit()

        return True
    
    return False



def is_admin_revoked(admin_id: int) -> bool:
    """
    Docstring for is_admin_approved_or_revoked
    
    :param admin_id: Description
    :type admin_id: int
    :return: Description
    :rtype: bool
    """
    admin = get_user_by_id(admin_id)

    if admin:
        admin.is_admin = False
        db.session.commit()

        return True
    
    return False