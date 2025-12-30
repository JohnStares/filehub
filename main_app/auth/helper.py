from flask_mail import Message
from main_app.extensions import mail
from secrets import token_hex

TOKEN: list[str] = []

def send_email(user_id: int, receiver: str) -> None:
    token = password_reset_token(user_id)
    msg = Message(
        subject="Password Reset",
        recipients=[receiver],
        body=f"Here is your password reset token\n{token}\nNote: Token invalidates after 15 mins."
    )

    try:
        mail.send(msg)
    except Exception:
        raise


def password_reset_token(user_id: int) -> str:
    if not isinstance(user_id, int):
        raise TypeError(f"Expects an int but got {type(user_id)}")

    token =  f"{user_id}_{token_hex(16)}"
    TOKEN.append(token)

    return token


def validate_token(token: str) -> bool:
    if not isinstance(token, str):
        raise ValueError(f"Token is expected to be a string but got {type(token)}")
    
    if token in TOKEN:
        return True
    
    return False