from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.validators import ValidationError
import sqlalchemy as sql

from main_app.extensions import db
from main_app.models import User
from main_app.validation import is_username_validated

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password1", message="Password does not match")])

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        if not is_username_validated(username.data):
            raise ValidationError("Please provide a valid username.")
        
        user = db.session.scalar(sql.select(User).where(User.username == username.data))
        
        if user is not None:
            raise ValidationError("Please choose another username")
        

    def validate_email(self, email):
        user = db.session.scalar(sql.select(User).where(User.email == email.data))

        if user is not None:
            raise ValidationError("Email already exist. Please use a different email")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
        

    def validate_password(self, password_field):
        user = db.session.scalar(sql.select(User).where(User.username == self.username.data))
        
        if user is None:
            raise ValidationError("Username or password not correct.")
            
        if not User.check_password(user, password_field.data):
            raise ValidationError("Username or password not correct")
        
        self.user = user

    submit = SubmitField("Login")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old_Password", validators=[DataRequired()])
    new_password = PasswordField("new_password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Please type same password as the above"), EqualTo("new_password", message="Password does not match")])

    submit = SubmitField("Submit")


class ForgetPassword(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(
                "Invalid email."\
                "Please provide a valid email address.",
                False, True, True, True
            )
        ]
    )
    submit = SubmitField("Send Reset Link")

class PasswordReset(FlaskForm):
    new_password = PasswordField("New Password", validators=[DataRequired(message="Password is required")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Please type same password as the above"), EqualTo("new_password", message="Password does not match")])

    submit = SubmitField()


class AdminRegisterForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Invalid email")])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password1", "Password does not match")])

    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        if not is_username_validated(username.data):
            raise ValidationError("Please provide a valid username")
        
        user = db.session.scalar(sql.select(User).where(User.username == username.data))

        if user:
            raise ValidationError("Please choose another name")
        
    def validate_email(self, email):
        user = db.session.scalar(sql.select(User).where(User.email == email.data))

        if user:
            raise ValidationError("Please provide another email")
        


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    submit = SubmitField("Sign In")

    def validate_password(self, password):
        if self.username.data and self.password.data:
            user = db.session.scalar(sql.select(User).where(User.username == self.username.data))

            if not user or user is None:
                raise ValidationError("Username or password is incorrect")
            
            if not User.check_password(user, password.data):
                raise ValidationError("Username or password is incorrect.")

            self.user = user