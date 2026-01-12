from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sql

from main_app.models import User
from main_app.extensions import db


class RegisterUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Invalid email address")])
    password1 = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password1", "Password doesn't match")])

    submit = SubmitField()

    def validate_username(self, username):
        user = db.session.scalar(sql.select(User).where(User.username == username.data))

        if user:
            raise ValidationError("Please provide another username")
        
    def validate_email(self, email):
        user = db.session.scalar(sql.select(User).where(User.email == email.data))

        if user:
            raise ValidationError("Please provide another email")



class EditUser(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email("Invalid email")])

    submit = SubmitField("Update")
