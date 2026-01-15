from flask import request, render_template, url_for, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required

from main_app.models import User, ResetToken
from main_app.extensions import db, login_manager, limiter
import sqlalchemy as sql
from secrets import token_hex

from . import auth_bp

from .forms import RegisterForm, LoginForm, ChangePasswordForm, ForgetPassword, PasswordReset, AdminLoginForm, AdminRegisterForm
from .helper import send_email, validate_token, save_token, AdminNotApproved
from .logic import process_admin_login, process_admin_registration

login_manager.login_view = "auth_bp.sign_in"


@auth_bp.route("/sign-up", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def sign_up():
    form = RegisterForm()

    if request.method == "POST":
        try:
            current_app.logger.info("A post request is being made to the sign-up route")
            if form.validate_on_submit():
                user = User(username=form.username.data, email=form.email.data)
                user.hash_password(form.password1.data)

                db.session.add(user)
                db.session.commit()

                flash("Registration Successful.", "success")
                current_app.logger.info(f"A successful sign-up was made by {form.username.data}")
                return redirect(url_for("auth_bp.sign_in"))
            

            flash("Invalid form input", "error")
            current_app.logger.warning("User made an invalid input while signing-up")
            return render_template("auth/register.html", form=form)
        
        except Exception as e:
            flash("Something wrong occured.", "error")
            db.session.rollback()
            current_app.logger.error(f"Unexpected error occured in the sign-up route", exc_info=True)
            return render_template("auth/register.html", form=form)
    
    current_app.logger.info("Sign-up route accessed")
    return render_template("auth/register.html", form=form)



@auth_bp.route("/sign-in", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def sign_in():
    form = LoginForm()
    if request.method == "POST":
        try:
            current_app.logger.info("A post request is being made to the sign-in route")
            if current_user.is_authenticated:
                return redirect(url_for("main_bp.home"))
            
            if form.validate_on_submit():
                user = form.user

                flash("Login Sucessful", "success")
                login_user(user)
                current_app.logger.info(f"A successful sign-in was made by {user.username}")
                return redirect(url_for("main_bp.home"))

            flash("Invalid username or password", "error")
            current_app.logger.warning(f"An invalid input made while trying to sign-in in the sign-up page")
            return render_template("auth/login.html", form=form)
        
        except Exception as e:
            flash("An error occured! Try again later", "error")
            current_app.logger.error(f"{user.username} got an unexpected error that occured in the sign-in route due to {str(e)}", exc_info=True)
            return render_template("auth/login.html", form=form)

    current_app.logger.info("Sign-in route accessed")
    return render_template("auth/login.html", form=form)



@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        user = current_user.username
        logout_user()
        flash("Logged out successfully.","success")
        current_app.logger.info(f"Successful logging out by {user}")
        return redirect(url_for("auth_bp.sign_in"))
    
    except Exception as e:
        flash("An error occured while trying to log you out", "warning")
        current_app.logger.error(f"An unexpected error occured while trying to log out {user} due to {str(e)}", exc_info=True)
        return redirect(url_for("auth_bp.sign_in"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per hour")
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST':
        current_app.logger.info(f"{current_user.username} made a post request on the change password route")
        try:
            if form.validate_on_submit():
                user = db.session.scalar(sql.select(User).where(User.username == current_user.username))

                if user:
                    if not user.check_password(form.old_password.data):
                        flash("Old password is incorrect.", "warning")
                        current_app.logger.info(f"{current_user.username} provided an incorrect password on the change password route")
                        return render_template("auth/changepassword.html", form=form)
                    
                    user.hash_password(form.new_password.data)
                    db.session.commit()

                    flash("Password changed successfully.", "success")
                    current_app.logger.info(f"{current_user.username} successfully changed their password")
                    return redirect(url_for("main_bp.home"))
                
                flash("Please Login again.", "error")
                current_app.logger.warning(f"{current_user.username} seems to not be a user. Being redirected to the sign-up page")
                return redirect(url_for("auth_bp.sign-in"))
            
            flash("An error occured with the data you provided.", "warning")
            current_app.logger.warning(f"{current_user.username} provided wrong information on the change password route")
            return render_template("auth/changepassword.html", form=form)
        
        except Exception as e:
            current_app.logger.error(f"{current_user.username} encountered an error on the change password route due to {str(e)}", exc_info=True)
            flash("An error occured! Please try again after sometime.", "warning")
            return render_template("auth/changepassword.html", form=form)
            
    current_app.logger.info(f"{current_user.username} accessed the change password page")
    return render_template("auth/changepassword.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def forgot_password():
    form = ForgetPassword()
    if request.method == "POST":
        try:
            current_app.logger.info("A post request was made to the forgot-password route")
            if form.validate_on_submit():
                user = db.session.scalar(sql.select(User).where(User.email == form.email.data))

                if user:
                    token = token_hex(26)
                    save_token(user.id, token, current_app)
                    send_email(receiver=form.email.data, token=token, host_url=request.host_url.rstrip("/"))
                    current_app.logger.info(f"Email has being sent to {form.email.data} that belongs to {user.username}")
                else:
                    current_app.logger.warning(f"User provided a wrong username in the forgot-password route. Email - {form.email.data}")
                
                flash(
                    "If email is registered with us, check your email.",
                    "success"
                )
                return redirect(url_for("auth_bp.forgot_password"))
            
            flash("Invalid input.", "warning")
            current_app.logger.info(
                f"Invalid input on the forgot-password route. input-{form.errors}"
            )
            return render_template("auth/forget-password.html", form=form)
            
        except Exception as e:
            flash("An error occured", "error")
            db.session.rollback()
            current_app.logger.error(f"An error occured on forget-password route due to {str(e)}", exc_info=True)
            return render_template("auth/forget-password.html", form=form)

    current_app.logger.info("The forget password route is being accessed")
    return render_template("auth/forget-password.html", form=form)


@auth_bp.route("/reset-password/<string:token>", methods=["GET", "POST"])
@limiter.limit("7 per hour")
def reset_password(token: str):
    form = PasswordReset()

    if request.method == "POST":
        try:
            current_app.logger.info("A post request is made on reset-password route")
            valid, user_id = validate_token(token)
            if not valid:
                flash("Invalid Reset Link", "error")
                current_app.logger.warning(f"An invalid reset link was provided in the reset_password route. Token - {token}")
                return render_template("auth/password-reset.html", form=form, token=token)
            
            if form.validate_on_submit():

                user = db.session.scalar(sql.select(User).where(User.id == user_id))

                if not user:
                    flash("You are not who you say you are", "error")
                    current_app.logger.warning(f"User couldn't be found on the token provided. The ID is {user_id}")
                    return redirect(url_for("auth_bp.sign_in"))
                
                user.hash_password(form.new_password.data)
                db.session.commit()
                flash("Password reset successfully", "success")
                current_app.logger.info(f"Successfully changed user with {user_id} password")
                ResetToken.delete_successfully_used_token(token)
                return redirect(url_for("auth_bp.sign_in"))
            
            flash("Invalid input", "warning")
            current_app.logger.info(f"Incorrect input on reset-password route. Error - {form.errors}")
            return render_template("auth/password-reset.html", form=form)
        
        except Exception as e:
            flash("An error occured", "error")
            current_app.logger.error(f"An unexpected error occured due to {str(e)}", exc_info=True)
            return render_template("auth/password-reset.html", form=form)

    return render_template("auth/password-reset.html", form=form, token=token)


@auth_bp.route("/admin/sign-up", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_sign_up():
    form = AdminRegisterForm()
    if request.method == "POST":
        current_app.logger.info("A post request is being made to the admin sign-up route")
        try:
            if not process_admin_registration(form):
                flash("Invalid input", "warning")
                current_app.logger.info(f"Invalid input was provided in the admin sign-up route. error: {form.errors}")
                return render_template("auth/admin-sign-up.html", form=form)
            
            flash("Registration Successful", "success")
            current_app.logger.warning(f"Successfully {form.username.data} as an admin")
            return redirect(url_for("auth_bp.admin_sign_in")) 
        
        except Exception as e:
            flash("An error occur. Try again!", "error")
            print("This caused the error", str(e))
            current_app.logger.error(f"An unexpected error occured in the admin sign-up due to {str(e)}", exc_info=True)
            return render_template("auth/admin-sign-up.html", form=form)
    
    current_app.logger.info("The admin sign-up route is being accessed")
    return render_template("auth/admin-sign-up.html", form=form)


@auth_bp.route("/admin/sign-in", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_sign_in():
    form = AdminLoginForm()
    if request.method == "POST":
        current_app.logger.info("A post request is being made to the admin sign-in route")
        try:
            if not process_admin_login(form):
                flash("Invalid input", "warning")
                current_app.logger.info(f"Invalid input was provided in the admin sign-in route. error: {form.errors}")
                return render_template("auth/admin-sign-in.html", form=form)
            
            flash("Sign in Successful", "success")
            current_app.logger.warning(f"Successfully {form.username.data} as an admin")
            return redirect(url_for("admin_bp.dashboard"))
        
        except AdminNotApproved:
            flash("You are not approved to be an Admin", "error")
            current_app.logger.info(f"{form.username.data} tried to login as a non approved admin")
            return render_template("auth/admin-sign-in.html", form=form)
        
        except Exception as e:
            flash("An error occur. Try again!", "error")
            current_app.logger.error(f"An unexpected error occured in the admin sign-in due to {str(e)}", exc_info=True)
            return render_template("auth/admin-sign-in.html", form=form)

    current_app.logger.info(f"The admin sign-in route is being accessed")  
    return render_template("auth/admin-sign-in.html", form=form)

