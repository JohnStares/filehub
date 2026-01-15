from flask_mail import Message
from main_app.extensions import mail, db
from main_app.models import ResetToken
import sqlalchemy as sql
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template
from typing import Literal

def send_email(receiver: str, token: str, host_url: str) -> None:

    html_body = render_template("main/email.html", host_url=host_url, token=token)

    # Plain text fallback
    text_body = f"""
        FileHub - Password Reset Request

        Hello!

        We received a request to reset your password for your FileHub account.

        Reset your password by visiting this link:
        {host_url}/auth/reset-password/{token}

        ⏰ IMPORTANT: This link will expire in 10 minutes for security reasons.

        Security Tips:
        ✓ Never share your password with anyone
        ✓ Use a strong, unique password
        ✓ If you didn't request this reset, please ignore this email

        If you didn't request a password reset, you can safely ignore this email. 
        Your password will remain unchanged.

        ---
        This is an automated message from FileHub
        Need help? Visit {host_url}

        © 2026 FileHub. All rights reserved.
    """

    msg = Message(
        subject="Password Reset - FileHub",
        recipients=[receiver],
        body=text_body,
        html=html_body
    )

    try:
        mail.send(msg)
    except Exception:
        raise


def save_token(user_id: int, token: str, current_app: Flask) -> None:
    if not isinstance(user_id, int):
        try:
            user_id = int(user_id)
        except ValueError:
            raise

    if not isinstance(token, str):
        try:
            token =  str(token)
        except ValueError:
            raise
    
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    try:
        new_token = ResetToken(user_id=user_id, token=token, expires_at=expires_at)
        db.session.add(new_token)
        db.session.commit()
        current_app.logger.info(f"New token saved to {user_id} with a token {token}")

    except Exception as e:
        current_app.logger.error(f"An error occured while saving token {token} to user {user_id} due to {str(e)}", exc_info=True)
        raise


def validate_token(token: str) -> (tuple[Literal[True], int] | tuple[Literal[False], None]):
    if not isinstance(token, str):
        try:
            token = str(token)
        except ValueError:
            raise

    token_obj = db.session.scalar(sql.select(ResetToken).where(ResetToken.token == token))

    if token_obj and token_obj.is_valid():
        return (True, token_obj.user_id)
    
    return (False, None)



class AdminNotApproved(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)