from flask import request, render_template, url_for, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required

from main_app.models import User
from main_app.extensions import db, login_manager, limiter
import sqlalchemy as sql

from . import auth_bp

from .forms import RegisterForm, LoginForm, ChangePasswordForm, ForgetPassword, PasswordReset
from .helper import send_email, validate_token

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
        current_app.logger.error(f"An unexpected error occured while trying to log out {current_user.username} due to {str(e)}", exc_info=True)
        return redirect(url_for("auth_bp.sign_in"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
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
            return redirect(url_for("main_bp.home"))
        
        except Exception as e:
            current_app.logger.error(f"{current_user.username} encountered an error on the change password route due to {str(e)}", exc_info=True)
            flash("An error occured! Please try again after sometime.", "warning")
            return redirect(url_for("main_bp.home"))
            
    current_app.logger.info(f"{current_user.username} accessed the change password page")
    return render_template("auth/changepassword.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgetPassword()
    if request.method == "POST":
        current_app.logger.info("A post request was made to the forgot-password route")
        if form.validate_on_submit():
            try:
                user = db.session.scalar(sql.select(User).where(User.username == form.username.data))

                if not user:
                    current_app.logger.warning("User provided a wrong username in the forgot-password route")
                    flash("Invalid username", "warning")
                    return redirect(url_for("auth_bp.forgot_password"))
                
                send_email(user.id, form.email.data)
                flash("Email Sent", "success")
                current_app.logger.info(f"Email has being sent to {form.email.data} that belongs to {user.username}")
                return redirect(url_for("auth_bp.token_validate"))
            
            except Exception as e:
                flash("An error occured", "error")
                current_app.logger.error(f"An error occured on forget-password route due to {str(e)}", exc_info=True)
                return redirect(url_for("auth_bp.forgot_password"))

    current_app.logger.info("The forget password route is being accessed")
    return render_template("auth/forget-password.html", form=form)


@auth_bp.route("/token-validate", methods=["GET", "POST"])
def token_validate():
    if request.method == "POST":
        current_app.logger.info("A post request is being made to the token-validate route")
        token = request.form.get("token")

        try:
            if not token:
                flash("Token cant be empty", "warning")
                current_app.logger.warning("An empty token was provided in the token-validate route")
                return redirect(url_for("auth_bp.token_validate"))

            if not validate_token(token):
                flash("Invalid Token", "error")
                current_app.logger.warning(f"An invalid token was provided in the token-validate route. Token - {token}")
                return redirect(url_for("auth_bp.token_validate"))
            
            current_app.logger.info(f"Token passed validation. Token - {token}")
            return redirect(url_for(f"auth_bp.reset_password", token=token))
        
        except Exception as e:
            flash("An error occured", "error")
            current_app.logger.error(f"An unexpected error occured due to {str(e)}")
            return redirect(url_for("auth_bp.sign_in"))
    
    current_app.logger.info("token-validate route is being accessed")
    return render_template("auth/token.html")



@auth_bp.route("/reset-password/<string:token>", methods=["GET", "POST"])
def reset_password(token: str):
    form = PasswordReset()
    form.token.data = token

    if request.method == "POST":
        try:
            current_app.logger.info("A post request is made on reset-password route")
            if form.validate_on_submit():
                token_parts = token.split("_")
                user_id = token_parts[0]

                user = db.session.scalar(sql.select(User).where(User.id == int(user_id)))

                if not user:
                    flash("You are not who you say you are", "error")
                    current_app.logger.warning(f"User couldn't be found on the token provided. The ID is {user_id}")
                    return redirect(url_for("auth_bp.sign_in"))
                
                user.hash_password(form.new_password.data)
                db.session.commit()
                flash("Password reset successfully", "success")
                current_app.logger.info(f"Successfully changed user with {user_id} password")
                # Dont' foret to remove the token from the TOKEN
                return redirect(url_for("auth_bp.sign_in"))
            
            flash("Invalid input", "warning")
            current_app.logger.info(f"Incorrect input on reset-password route. Error - {form.errors}")
            return redirect(url_for("auth_bp.reset-password"))
        
        except Exception as e:
            flash("An error occured", "error")
            current_app.logger.error(f"An unexpected error occured due to {str(e)}", exc_info=True)
            return redirect(url_for("auth_bp.sign_in"))

    return render_template("auth/password-reset.html", form=form)