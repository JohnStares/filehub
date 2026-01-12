import sqlalchemy as sql
import sqlalchemy.orm as orm
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime, timezone

from .extensions import db
from .extensions import login_manager

from typing import Optional

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sql.String(20), unique=True, index=True, nullable=False)
    email: orm.Mapped[str] = orm.mapped_column(sql.String(30), unique=True, index=True, nullable=False)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sql.String(300))

    # Ensures when a user is deleted, all of itself is removed from the database that referenced it
    sections: orm.Mapped[list["Section"]] = orm.relationship(
        "Section",
        back_populates="user",
        cascade="all, delete-orphan" # Remember to change to passive_deletes=True in proudction
    )


    def hash_password(self, password: str):
        """This method takes in a password in string format and hashes it securely"""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str):
        """Checks if the provided password matches that already stored. Returns False if it doesn't match"""
        if self.password_hash is not None:
            return check_password_hash(self.password_hash, password)
        

    @classmethod
    def create_user(cls, username: str, email: str, password: str, **kwargs) -> None:
        """
        This function provides another way to create a user
        
        :param username: A unique name that serves as a username for the user
        :type username: str
        :param email: A unique and valid email
        :type email: str
        :param password: A very strong password
        :type password: str
        :param **kwargs: Other keyword arguments
        :type **kwargs: dict
        """
        user = cls(username=username, email=email)
        user.hash_password(password)

        db.session.add(user)
        db.session.commit()


    def __str__(self):
        return f"Username: {self.username} | Email: {self.email}"



class Section(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(User.id, name="fk_section_user_id"), index=True)
    section_name: orm.Mapped[str] = orm.mapped_column(sql.String(30), index=True, unique=True)
    section_code: orm.Mapped[str] = orm.mapped_column(sql.String(15), index=True, unique=True, nullable=True)
    expected_submission: orm.Mapped[int] = orm.mapped_column(sql.Integer, index=True, nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))


    # Backdoor to User
    user: orm.Mapped["User"] = orm.relationship("User", back_populates='sections')

    # This relationship ensure that when a section is deleted, it removes itself from the submissions table
    submissions: orm.Mapped[list["Submissions"]] = orm.relationship(
        "Submissions",
        back_populates="section",
        cascade="all, delete-orphan" # Remember to change to passive_deletes=True in proudction
    )


    def __str__(self) -> str:
        return f"Section: {self.section_code}-{self.section_name} Exp_sub-{self.expected_submission}"
    


class Submissions(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    section_id: orm.Mapped[int] = orm.mapped_column(sql.ForeignKey(Section.id, name="fk_submission_section_id", ondelete="CASCADE"), index=True)
    uploader_name: orm.Mapped[str] = orm.mapped_column(sql.String(30), index=True)
    mat_no: orm.Mapped[str] = orm.mapped_column(sql.String(10), nullable=True)
    level: orm.Mapped[str] = orm.mapped_column(sql.String(10), nullable=True)
    group: orm.Mapped[str] = orm.mapped_column(sql.String(20), nullable=True)
    original_filename: orm.Mapped[str] = orm.mapped_column(sql.String(30))
    stored_filename: orm.Mapped[str] = orm.mapped_column(sql.String(30))
    file_path: orm.Mapped[str] = orm.mapped_column(sql.String(250), index=True, unique=True)
    file_size: orm.Mapped[int] = orm.mapped_column(sql.Integer)
    uploaded_at: orm.Mapped[datetime] = orm.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    # Establishes a backdoor to Section
    section: orm.Mapped["Section"] = orm.relationship("Section", back_populates="submissions") 


    def __str__(self) -> str:
        return f"Filename: {self.original_filename} by {self.uploader_name} at {self.uploaded_at}"
    


class ResetToken(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, index=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sql.Integer, index=True)
    token: orm.Mapped[str] = orm.mapped_column(sql.String(70), unique=True, index=True)
    expires_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), index=True)
    used: orm.Mapped[bool] = orm.mapped_column(sql.Boolean, default=False)
    time_created: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def is_valid(self) -> bool:
        """
        Returns true if the time is still within time frame
        """
        if self.expires_at.tzinfo is None:
            expires_at_aware = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = self.expires_at

        return datetime.now(timezone.utc) < expires_at_aware
    
    @classmethod
    def mark_expired_token_as_used(cls) -> None:
        """
        Marks unused and expired token as used
        """

        unused_token: list[ResetToken] = cls.query.filter(cls.used == False).all()

        expired_unused_token = [
            token for token in unused_token \
            if datetime.now(timezone.utc) <= token.expires_at.replace(tzinfo=timezone.utc)
        ]

        for token in expired_unused_token:
            token.used = True
        db.session.commit()

    @classmethod
    def delete_successfully_used_token(cls, token: str) -> None:
        """
        Deletes tokens that are successfully used.
        """
        used_token = cls.query.filter(cls.token == token).first()

        db.session.delete(used_token)
        db.session.commit()


    @classmethod
    def delete_used_token(cls) -> None:
        """
        Deletes all used token.
        """
        used_token: list[ResetToken] = cls.query.filter(cls.used == True).all()

        for token in used_token:
            db.session.delete(token)
        
        db.session.commit()


    def __str__(self) -> str:
        return f"ResetToken: User_id-{self.user_id} || Token-{self.token} || Expires_at-{self.expires_at}"


# flask-login uses this to know to load a user
@login_manager.user_loader
def load_user(id):
    """Returns an instance of a user that has that id passed as an argument."""
    return db.session.get(User, int(id))