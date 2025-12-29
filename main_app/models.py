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
    
    

# flask-login uses this to know to load a user
@login_manager.user_loader
def load_user(id):
    """Returns an instance of a user that has that id passed as an argument."""
    return db.session.get(User, int(id))