import sqlalchemy as sql
from flask import current_app

from typing import Sequence

from main_app.models import User, Section, Submissions, Message
from main_app.extensions import db
from main_app.admin.exception import MessageDoesNotExist


def get_total_users() -> int | None:
    """
    This function returns the total count of all users in the database

    :rtype: int | None
    """
    users_count = db.session.scalar(sql.select(sql.func.count()).select_from(User))

    return users_count

def get_non_admin_count() -> int | None:
    """
    This returns the total number of users that are not admin

    :rtype: int | None
    """
    non_admin = db.session.scalar(sql.select(sql.func.count()).select_from(User).where(User.role == "user"))

    return non_admin

def get_admin_count() -> int | None:
    """
    Returns the total count of admins

    :rtype: int | None
    """
    admin = db.session.scalar(sql.select(sql.func.count()).select_from(User).where(User.role == "admin"))

    return admin


def get_all_users() -> Sequence[User]:
    """
    This returns all the users in the database

    :rtype: Sequence[User]
    """
    users = db.session.scalars(sql.select(User)).all()

    return users


def delete_user(id: int) -> None:
    """
    Deletes a user by id
    
    :param id: user id
    :type id: int
    """
    user = db.session.get(User, id)

    if user is not None:
        db.session.delete(user)
        db.session.commit()



def get_user_by_id(id: int) -> User | None:
    """
    Gets a user by ID
    
    :param id: ID of the user
    :type id: int
    :return: A user object if user or none
    :rtype: User | None
    """
    user = db.session.get(User, id)

    return user


def get_user_by_name(username: str) -> User | None:
    """
    Gets a user by username
    
    :param username: Username of the user
    :type username: str
    :return: A user object if user or None
    :rtype: User | None
    """

    user = db.session.scalar(sql.select(User).where(User.username == username))

    return user


def get_user_by_email(email: str) -> User | None:
    """
    Gets a user by email
    
    :param email: user email
    :type email: str
    :return: A user object if user or none
    :rtype: User | None
    """
    user = db.session.scalar(sql.select(User).where(User.email == email))

    return user

def filter_user_by_role(role: str) -> Sequence[User]:
    """
    Search and returns users that meet the specific role
    
    :param role: Role of the user either admin or user
    :type role: str
    :return: A list or sequences of users
    :rtype: Sequence[User]
    """
    users = db.session.scalars(sql.select(User).filter(User.role == role)).all()

    return users


def get_user_section(id: int) -> Section | None:
    """
    Returns the section of the user
    
    :param id: ID of a section
    :type id: int
    :return: A sequence of sections
    :rtype: Sequence[Section]
    """
    section = db.session.get(Section, id)

    if section is not None:
        return section
    
    return None


def get_user_submissions(section_id: int, page_num: int):
    """
    Docstring for get_user_submissions
    
    :param section_id: Description
    :type section_id: int
    :param page_num: Description
    :type page_num: int
    :return: Description
    :rtype: Sequence[Submissions] | None
    """
    query = sql.select(Submissions).where(Submissions.section_id == section_id)

    files = db.paginate(query, page=page_num, per_page=current_app.config["FILES_PER_PAGE"], error_out=False)

    return files


def get_user_file(id: int) -> Submissions | None:
    file = db.session.get(Submissions, id)

    if file is not None:
        return file
    
    return None


def is_section_deleted(section_id: int) -> bool:
    """
    Deletes a section
    
    :param section_id: ID of the section
    :type section_id: int
    """
    section = db.session.get(Section, section_id)

    if section:
        db.session.delete(section)
        db.session.commit()

        return True
    
    return False



def is_file_deleted(file_id: int) -> bool:
    """
    Deletes a file
    
    :param file_id: ID of the file
    :type file_id: int
    """
    file = db.session.get(Submissions, file_id)

    if file:
        db.session.delete(file)
        db.session.commit()

        return True
    
    return False


def get_user(info: str, filter: str) -> User |  None:
    if filter == "email":
        return get_user_by_email(info)
    else:
        return get_user_by_name(info)
    


def get_user_by_username_or_email(search: str) -> User | None:
    if "@" in search:
        print("Goint by this")
        print(search)
        return get_user_by_email(search)
    else:
        print("Going by that")
        return get_user_by_name(search)
    


def get_all_admins():
    return db.session.scalars(sql.select(User).where(User.role == "admin")).all()


def get_unread_message_count():
    """
    This counts all messages sent that are unread and returns the total count as an integer
    """
    unread_message_count = db.session.scalar(sql.select(sql.func.count()).select_from(Message).where(Message.read == False))

    return unread_message_count


def mark_message_as_read(message_id: int) -> bool:
    """
    This marks read messages as read
    
    :param message_id: Message ID you want to mark as read
    :type message_id: int
    :return: True if successfully marked else False
    :rtype: bool
    """
    message = db.session.get(Message, message_id)

    try:
        if message:
            message.read = True

            db.session.commit()

            return True
        
        raise MessageDoesNotExist(f"Message with ID {message_id} does not exist")
    
    except MessageDoesNotExist:
        raise 

    except Exception:
        raise Exception
    


def get_messages() -> Sequence[Message]:
    """
    Returns all messages
    
    :return: A sequence of messages
    :rtype: Sequence[Message]
    """

    messages = db.session.scalars(sql.select(Message)).all()

    return messages