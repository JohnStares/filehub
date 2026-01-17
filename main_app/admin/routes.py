from flask import redirect, render_template, request, current_app, url_for, flash
from main_app.extensions import limiter
from flask_login import login_required, current_user

from main_app.admin import admin_bp
from main_app.admin.validation import admin_required
from main_app.admin.helper import (
    get_user_submissions, get_user_by_email,
    get_user_section, filter_user_by_role, get_user_by_name, get_user_by_id, is_section_deleted,
    is_file_deleted, get_user_by_username_or_email, get_all_admins, get_unread_message_count, get_messages,
    mark_message_as_read, count
)  

from main_app.admin.logic import (
    user_deleted, paginate_users, registered_user, is_user_edited, is_admin_approved, is_admin_revoked
)

from main_app.admin.forms import RegisterUserForm, EditUser

from main_app.admin.exception import CannotDeleteAdmin, UserAlreadyExist, EmailAlreadyExist, MessageDoesNotExist


@admin_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
@admin_required
def dashboard():
    try:
        search = request.args.get("search")
        filter = request.args.get("filter")

        page = request.args.get("page", 1, type=int)

        users = paginate_users(page)

        next_url = url_for("admin_bp.dashboard", page=users.next_num) \
            if users.has_next else None
        
        prev_url = url_for("admin_bp.dashboard", page=users.prev_num) \
            if users.has_prev else None

        if search and filter:
            current_app.logger.info(f"{current_user.username}:: Searched for {search} in {filter}")

        counts = count()

        data = {
            "users": counts.total_users if counts else 0,
            "non_admin": counts.non_admin if counts else 0,
            "admin": counts.admin if counts else 0,
            "all_users": users,
            "user_by_name": get_user_by_name(search.strip()) if search is not None and filter == "name"  else None,
            "user_by_email": get_user_by_email(search.strip()) if search is not None and filter == "email" else None,
            "unread_mails": get_unread_message_count(),
            "unread_notifications": 4,
            "user_by_role": filter_user_by_role(search.strip()) if search is not None and filter == "role" else None,
            "next": next_url,
            "prev": prev_url
        }

        current_app.logger.info(f"{current_user.username}:: Accessed the dashboard page")
        return render_template("admin/dashboard.html", data=data)
    
    except Exception as e:
        flash("An error occured. Please try again later!", "error")
        return redirect(url_for("main_bp.welcome"))



@admin_bp.route("/create-user", methods=["GET","POST"])
def create_user():
    form = RegisterUserForm()

    if request.method == 'POST':
        try:
            if not registered_user(form):
                flash("Invalid input", "warning")
                current_app.logger.info(f"{current_user.username}:: Inputted an invalid input while trying to register a user")
                return render_template("admin/create-user.html", form=form)
            
            flash("User registered successfully", "success")
            current_app.logger.info(f"{current_user.username}:: Registered {form.username.data}")
            return redirect(url_for("admin_bp.create_user"))
    
        except Exception as e:
            flash("An error occured. Please try again later!", "error")
            current_app.logger.error(f"{current_user.username} got an unexpected error while trying to register {form.username.data} due to {str(e)}", exc_info=True)
            return render_template("admin/create-user.html", form=form)
        
    current_app.logger.info(f"{current_user.username}:: Accessed the create_route")
    return render_template("admin/create-user.html", form=form)


@admin_bp.route("/edit-user/<int:user_id>", methods=["GET","POST"])
def edit_user(user_id):
    try:
        search = request.args.get("search")
        if search:
            user = get_user_by_username_or_email(search.strip())
        else:
            user = get_user_by_id(user_id)

        if not user:
            flash("No user found")
            current_app.logger.info(f"{current_user.username} got a user not found on the search paramater {search}")
            return redirect(url_for("admin_bp.dashboard"))

        form = EditUser(obj=user)

        if request.method == "POST":
            try:
                if not is_user_edited(form, user):
                    flash("Invalid input", "warning")
                    current_app.logger.info(f"{current_user.username}:: Got a form error while editing {user.username} details due to {form.errors}")
                    return render_template("admin/edit-user.html", form=form, user=user)
                
                flash("User edited successfully", "success")
                current_app.logger.info(f"{current_user.username}:: Successfully eidted {user.username} details")
                return redirect(url_for("admin_bp.user_details", user_id=user.id))
            
            except UserAlreadyExist:
                flash("Username already exist", "warning")
                current_app.logger.info(f"{current_user.username} got a User already exit error while trying to edit {user.username} details")
                return render_template("admin/edit-user.html", form=form, user=user)
            
            except EmailAlreadyExist:
                flash("Email already exist", "warning")
                current_app.logger.info(f"{current_user.username} got a Email already exit error while trying to edit {user.username} details")
                return render_template("admin/edit-user.html", form=form, user=user)
            
        current_app.logger.info(f"{current_user.username} Accessed the edit-user route to edit {user.username} details")
        return render_template("admin/edit-user.html", form=form, user=user)
    
    except Exception as e:
        flash("An error occured. Please try again!", "error")
        current_app.logger.error(f"{current_user.username} got an error while trying to update user with ID {user_id} details", exc_info=True)
        return render_template("admin/edit-user.html", form=form, user=user)



@admin_bp.route("/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id: str):
    try:
        if not user_deleted(user_id=user_id):
            flash("Can't delete user", "error")
            current_app.logger.info(f"{current_user.username}:: Having difficulty deleting user with ID {user_id}")
            return redirect(url_for("admin_bp.user_details", user_id=user_id))
        
        flash("Successfully deleted user", "success")
        current_app.logger.info(f"{current_user.username}:: Successfully deleted user with ID {user_id}")
        return redirect(url_for("admin_bp.dashboard"))
    
    except CannotDeleteAdmin:
        flash("Can't delete admin", "warning")
        current_app.logger.info(f"{current_user.username}:: tried deleting an admin with ID {user_id}")
        return redirect(url_for("admin_bp.user_details", user_id=user_id))
    
    except Exception as e:
        flash("An unexpected error occured", "error")
        current_app.logger.error(f"An error occured while {current_user.username} was trying to delete user with ID {user_id} due to {str(e)}", exc_info=True)
        return redirect(url_for("admin_bp.dashboard"))




@admin_bp.route("/settings", methods=["GET","POST"])
def settings():
    pass



@admin_bp.route("/mails", methods=["GET"])
@login_required
@admin_required
def mails():
    data = {
        "messages": get_messages()
    }
    return render_template("admin/mails.html", data=data)



@admin_bp.post("/mark-read-messages/<int:message_id>")
@login_required
@admin_required
def mark_message_read(message_id: int):
    try:
        if not mark_message_as_read(message_id=message_id):
            flash("Could not mark message as read", "error")
            return redirect(url_for('admin_bp.mail'))
        
        flash("Message marked as read", "success")
        return redirect(url_for('admin_bp.mails'))
    
    except MessageDoesNotExist:
        flash("Somehow message doesn't exist", "error")
        return redirect(url_for('admin_bp.mails'))
    
    except Exception as e:
        flash("An unexpected error occured", "error")
        return redirect(url_for("admin_bp.mails"))


@admin_bp.post("/delete-messages")
@login_required
@admin_required
def delete_all_read_messages():
    ...


@admin_bp.post("/delete/message/<int:message_id>")
@login_required
@admin_required
def delete_message(message_id: int):
    ...


@admin_bp.route("/profile/<int:user_id>", methods=["GET","POST"])
def profile(user_id):
    data = {
        "admin": get_user_by_id(user_id)
    }
    current_app.logger.info(f"{current_user.username} accessed the profile route.")
    return render_template("/admin/admin-profile.html", data=data)


@admin_bp.route("/user-details/<int:user_id>", methods=["GET"])
def user_details(user_id):
    current_app.logger.info(f"The get user-detail route is being accessed by {current_user.username} for user with ID {user_id}")
    user = get_user_by_id(int(user_id))

    data = {
        "user": user
    }

    if not user:
        flash("No user found", "warning")
        current_app.logger.warning(f"{current_user.username} tried searching for a user that doesn't exit with the ID {user_id}")
        return redirect(url_for("admin_bp.dashboard"))

    if user and current_user.id == user.id:
        return render_template("admin/user-detail.html", data=data)
        
    if user and current_user.role == "admin" and user.role in ["admin", "super_admin"]:
        flash("You can't view the content of other admins", "warning")
        current_app.logger.info(f"{current_user.username}:: Tried accessing an {user.role} page")
        return redirect(url_for("admin_bp.dashboard"))


    return render_template("admin/user-detail.html", data=data)


@admin_bp.route("/user-section/<int:section_id>", methods=["GET", "POST"])
@admin_required
def user_section(section_id: str):
    try:
        page = request.args.get("page", 1, type=int)

        section = get_user_section(int(section_id))

        # Don't forget to paginate this properly 

        paginated_files = get_user_submissions(section.id, page)

        next_url = url_for("admin_bp.user_section", section_id=section_id, page=paginated_files.next_num) \
            if paginated_files.has_next else None
        
        prev_url = url_for("admin_bp.user_section", section_id=section_id, page=paginated_files.prev_num) \
            if paginated_files.has_prev else None

        data = {
            "section": section,
            "files": paginated_files,
            "next": next_url,
            "prev": prev_url
        }

        current_app.logger.info(f"{current_user.username} accessed section page eitj ID {section.id}")
        return render_template("admin/user-section.html", data=data)
    
    except Exception as e:
        flash("An error occured. Please try again later", "error")
        current_app.logger.error(f"{current_user.username}::An unexpected error occured due to {str(e)}")
        return render_template("admin/user-section.html", data=data)



@admin_bp.route("/delete-section/<int:user_id>/<int:section_id>", methods=["POST"])
@admin_required
def delete_section(user_id, section_id):
    try:
        if not is_section_deleted(int(section_id)):
            flash("Unable to delete section", "error")
            current_app.logger.info(f"{current_user.username}:: Unable to delete section with the ID {section_id}")
            return redirect(url_for("admin_bp.user_section", section_id=section_id))
        
        flash("Section deleted successfully", "success")
        current_app.logger.info(f"{current_user.username}:: deleted section with the ID {section_id}")
        return redirect(url_for("admin_bp.user_details", user_id=user_id))
    
    except Exception as e:
        flash("An error occured. Please try again later!", "error")
        current_app.logger.info(f"An error occured while {current_user.username} is trying to delete section with ID {section_id}", exc_info=True)
        return redirect(url_for("admin_bp.user_details", user_id=user_id))



@admin_bp.route("/delete-file/<int:section_id>/<int:file_id>", methods=["POST"])
@admin_required
def delete_file(section_id, file_id):
    try:
        if not is_file_deleted(int(file_id)):
            flash("Unable to delete file", "error")
            current_app.logger.info(f"{current_user.username}:: Unable to delete file with the ID {file_id}")
            return redirect(url_for("admin_bp.user_section", section_id=section_id))
        
        flash("File deleted successfully", "success")
        current_app.logger.info(f"{current_user.username}:: deleted file with the ID {file_id}")
        return redirect(url_for("admin_bp.user_section", section_id=section_id))
    
    except Exception as e:
        flash("An error occured. Please try again later!", "error")
        current_app.logger.info(f"An error occured while {current_user.username} is trying to delete a file with ID {file_id}", exc_info=True)
        return redirect(url_for("admin_bp.user_section", section_id=section_id))
    



@admin_bp.route("/download-file/<int:section_id>/<int:file_id>", methods=["GET"])
@admin_required
def download_file(section_id, file_id):
    flash("Unauthorized", "error")
    current_app.logger.info(f"{current_user}:: Tried to dowload a user file with the ID {file_id}")
    return redirect(url_for("admin_bp.user_section", section_id=section_id))



@admin_bp.route("/manage-admins", methods=["GET"])
@admin_required
def manage_admins():
    data = {
        "admins": get_all_admins()
    }
    current_app.logger.info(f"{current_user.username}:: accessed the manage admin routes")
    return render_template("admin/modify-admin.html", data=data)



@admin_bp.route("/approve-admin/<admin_id>", methods=["POST"])
@admin_required
def approve_admin(admin_id):
    try:
        if not is_admin_approved(admin_id):
            flash("Couldn't approve admin", "warning")
            current_app.logger.info(f"{current_user.username}:: couldn't approve admin with the ID {admin_id} to have admin priviliges")
            return redirect(url_for("admin_bp.manage_admins"))
        
        flash("Approved admin", "success")
        current_app.logger.info(f"{current_user.username}:: approved admin with the ID {admin_id} to have admin priviliges")
        return redirect(url_for("admin_bp.manage_admins"))
    
    except Exception as e:
        flash("An error occured, Please Try again!", "error")
        current_app.logger.info(f"{current_user.username}:: got an error while trying to approve admin with the ID {admin_id} to have admin priviliges", exc_info=True)
        return redirect(url_for("admin_bp.manage_admins"))


@admin_bp.route("/revoke-admin/<admin_id>", methods=["POST"])
@admin_required
def revoke_admin(admin_id):
    try:
        if not is_admin_revoked(admin_id):
            flash("Couldn't revoke admin", "warning")
            current_app.logger.info(f"{current_user.username}::  couldn't revoked admin with the ID {admin_id} admin priviliges")
            return redirect(url_for("admin_bp.manage_admins"))
        
        flash("Revoked admin", "success")
        current_app.logger.info(f"{current_user.username}:: revoked admin with the ID {admin_id} admin priviliges")
        return redirect(url_for("admin_bp.manage_admins"))
    
    except Exception as e:
        flash("An error occured, Please Try again!", "error")
        current_app.logger.error(f"{current_user.username}:: got an error while trying to revoke admin with  ID {admin_id} privileges", exc_info=True)

        return redirect(url_for("admin_bp.manage_admins"))