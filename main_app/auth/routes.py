from flask import request, render_template, url_for, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required

from main_app.models import User
from main_app.extensions import db, login_manager, limiter

from . import auth_bp

from .forms import RegisterForm, LoginForm

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
                current_app.logger.info("A successful sign-up was made")
                return redirect(url_for("auth_bp.sign_in"))
            

            flash("Invalid form input", "error")
            current_app.logger.warning("User made an invalid input while signing-up")
            return render_template("auth/register.html", form=form)
        
        except Exception as e:
            flash("Something wrong occured.", "error")
            db.session.rollback()
            current_app.logger.exception(f"Unexpected error occured in the sign-up route", exc_info=True)
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
                current_app.logger.info("A successful sign-in was made")
                return redirect(url_for("main_bp.home"))

            flash("Invalid username or password", "error")
            current_app.logger.warning("User made an invalid input while signing-in")
            return render_template("auth/login.html", form=form)
        
        except Exception as e:
            flash("An error occured! Try again later", "error")
            current_app.logger.exception(f"Unexpected error occured in the sign-in route due to {str(e)}", exc_info=True)
            return render_template("auth/login.html", form=form)

    current_app.logger.info("Sign-in route accessed")
    return render_template("auth/login.html", form=form)



@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        flash("Logged out successfully.","success")
        current_app.logger.info("Successful logging out")
        return redirect(url_for("auth_bp.sign_in"))
    
    except Exception as e:
        flash("An error occured while trying to log you out", "warning")
        current_app.logger.exception(f"An unexpected error occured while trying to log out a user due to {str(e)}", exc_info=True)
        return redirect(url_for("auth_bp.sign-in"))