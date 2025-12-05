import pytest
from main_app.models import User, Section, Submissions
from main_app.extensions import db
import sqlalchemy as sql


class TestUserModel:
    def test_create_user(self, app, session):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")

            session.add(user)
            session.commit()

            assert user.id is not None
            assert user.username == "Empress_Stares"
            assert user.email == "empress@gmail.com"
            assert user.password_hash is not None


    def test_password_hashing(self, app, session):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")

            session.add(user)
            session.commit()

            assert user.password_hash is not None
            assert user.password_hash != "john123456"
            assert user.check_password("john123456") == True
            assert user.check_password("empress2345") == False


    def test_unique_username(self, app, session, sample_user):
        with app.app_context():
            user1 = User(
                username=sample_user.username,
                email="eather@gmail.com"
            )

            user1.hash_password("john123456")

            session.add(user1)

            with pytest.raises(Exception):
                session.commit()

            
    def test_unique_email(self, app, session, sample_user):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email=sample_user.email
            )

            user.hash_password("john123456")

            session.add(user)

            with pytest.raises(Exception):
                session.commit()


    def test_user_sections_relationship(self, app, session, sample_user):
        with app.app_context():
            section1 = Section(
                section_name="Assignment",
                section_code="ASS-2445",
                expected_submission=10,
                user_id=sample_user.id
            )

            session.add(section1)
            session.commit()


            section2 = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=sample_user.id
            )

            session.add(section2)
            session.commit()


            user = session.scalar(sql.select(User).where(User.username == sample_user.username))

            assert user is not None
            assert len(user.sections) == 2

            user_section = [s.section_name for s in user.sections]

            assert "Assignment" in user_section
            assert "Seminar" in user_section
            assert "Project" not in user_section


    def test_cascade_user_delete(self, app, session):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")

            session.add(user)
            session.commit()


            section = Section(
                    section_name="Assignment",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=user.id
                )

            session.add(section)
            session.commit()

            user = session.scalar(sql.select(User))
            section = session.scalar(sql.select(Section))

            assert user is not None
            assert section is not None

            session.delete(user)

            assert session.scalar(sql.select(User)) is None
            assert session.scalar(sql.select(Section)) is None


class TestSectionModel:
    def test_section_creation(self, app, session, sample_user):
        with app.app_context():
            section = Section(
                    section_name="Assignment",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=sample_user.id
                )

            session.add(section)
            session.commit()

            section = session.scalar(sql.select(Section).where(Section.section_name == "Assignment"))

            assert section is not None
            assert "Assignment" in section.section_name
            assert "Project" not in section.section_name


    def test_correct_section_user_relationship(self, app, session, sample_user):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            ) 

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            user1 = User(
                username="Raviva_Stares",
                email="raviva@gmail.com"
            ) 

            user1.hash_password("john123456")
            session.add(user1)
            session.commit()


            section1 = Section(
                    section_name="Assignment",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=user.id
                )

            session.add(section1)
            session.commit()

            section2 = Section(
                    section_name="Seminar",
                    section_code="SEM-2445",
                    expected_submission=10,
                    user_id=sample_user.id
                )

            session.add(section2)
            session.commit()

            section1 = session.scalar(sql.select(Section).where(Section.user_id == user.id))
            section2 = session.scalar(sql.select(Section).where(Section.user_id == sample_user.id))
            section3 = session.scalar(sql.select(Section).where(Section.user_id == user1.id))

            assert section1 is not None
            assert section2 is not None
            assert section3 is None

            assert "Assignment" in section1.section_name
            assert "Seminar" in section2.section_name


    def test_section_nullable_field(self, app, session, sample_user):
        with app.app_context():
            section = Section(
                section_name="Assignment",
                section_code=None,
                expected_submission=None,
                user_id=sample_user.id
            )

            session.add(section)
            session.commit()


            assert section.id is not None
            assert section.expected_submission is None
            assert section.section_code is None


    def test_section_submissions_relationship(self, app, session, sample_section):
        with app.app_context():
            submission = Submissions(
                section_id=sample_section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{sample_section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()

            submission1 = Submissions(
                section_id=sample_section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_project.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{sample_section.section_name}/john_stares_project.pptx",
                file_size=11143
            )

            session.add(submission1)
            session.commit()

            section = session.scalar(sql.select(Section))

            assert section is not None
            assert len(section.submissions) == 2

            submissions = [s.original_filename for s in section.submissions]

            assert "john_stares_seminar.pptx" in submissions
            assert "john_stares_project.pptx" in submissions


    def test_cascade_section_delete(self, app, session, sample_user):
        with app.app_context():
            section = Section(
                    section_name="Assignment",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=sample_user.id
                )

            session.add(section)
            session.commit()

            submission = Submissions(
                section_id=section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()


            user = session.scalar(sql.select(User))
            section = session.scalar(sql.select(Section))
            submission = session.scalar(sql.select(Submissions))

            assert user and section and submission is not None

            session.delete(section)

            assert session.scalar(sql.select(Section)) is None
            assert session.scalar(sql.select(Submissions)) is None



class TestSubmissonsModel:
    def test_create_submission(self, app, session, sample_section):
        with app.app_context():
            submission = Submissions(
                section_id=sample_section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{sample_section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()

            submission = session.scalar(sql.select(Submissions))

            assert submission is not None
            assert submission.section_id == sample_section.id
            assert submission.uploader_name == "John Stares"
            assert submission.uploader_name != "Empress Stares"
            assert submission.file_path is not None


    def test_submissions_nullable_fields(self, app, session, sample_section):
        with app.app_context():
            submission = Submissions(
                section_id=sample_section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=None,
                group=None,
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{sample_section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()

            submission = session.scalar(sql.select(Submissions))

            assert submission is not None

            assert submission.level is None
            assert submission.group is None

    
    def test_submission_not_nullable_fields(self, app, session, sample_section):
        with app.app_context():
            submission = Submissions(
                section_id=sample_section.id,
                uploader_name=None,
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename=None,
                stored_filename="john_stares_seminar.pptx",
                file_path=None,
                file_size=11141
            )

            session.add(submission)
            
            with pytest.raises(Exception):
                session.commit()


    def test_submission_section_relationship(self, app, session, sample_user):
        with app.app_context():
            section = Section(
                    section_name="Project",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=sample_user.id
                )

            session.add(section)
            session.commit()

            submission1 = Submissions(
                section_id=section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission1)
            session.commit()


            submission2 = Submissions(
                section_id=section.id,
                uploader_name="Empress Stares",
                mat_no="DE.2018/5151",
                level=200,
                group="ACADEMY_NERD",
                original_filename="empress_stares_seminar.pptx",
                stored_filename="empress_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/empress_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission2)
            session.commit()

            submissions = session.scalars(sql.select(Submissions).where(Submissions.section_id == section.id)).all()

            assert submissions is not None

            assert len(submissions) == 2
            assert all(sub.section_id == section.id for sub in submissions)


    def test_submission_correct_file_path(self, app, session, sample_section):
        with app.app_context():
            submission = Submissions(
                section_id=sample_section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{sample_section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()

            submission = session.scalar(sql.select(Submissions))

            assert submission is not None
            assert f"uploaded_files/{sample_section.section_name}/{submission.original_filename}" in submission.file_path



class TestModelRelationships:
    def test_user_submission_through_section(self, app, session):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")

            session.add(user)
            session.commit()


            section = Section(
                    section_name="Project",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=user.id
                )

            session.add(section)
            session.commit()

            submission1 = Submissions(
                section_id=section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission1)
            session.commit()


            submission2 = Submissions(
                section_id=section.id,
                uploader_name="Empress Stares",
                mat_no="DE.2018/5151",
                level=200,
                group="ACADEMY_NERD",
                original_filename="empress_stares_seminar.pptx",
                stored_filename="empress_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/empress_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission2)
            session.commit()

            submission3 = Submissions(
                section_id=section.id,
                uploader_name="Ravivaa Stares",
                mat_no="DE.2018/3151",
                level=200,
                group="ACADEMY_NERD",
                original_filename="raviva_stares_seminar.pptx",
                stored_filename="raviva_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/ravivastares_seminar.pptx",
                file_size=11141
            )

            session.add(submission3)
            session.commit()

            user = session.scalar(sql.select(User))

            assert user and section and submission3, submission1 and submission2 is not None

            user_submissions = []

            for section in user.sections:
                user_submissions.extend(section.submissions)

            assert len(user_submissions) == 3


    def delete_user_cascades(self, app, session):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")

            session.add(user)
            session.commit()


            section = Section(
                    section_name="Project",
                    section_code="ASS-2445",
                    expected_submission=10,
                    user_id=user.id
                )

            session.add(section)
            session.commit()

            section1 = Section(
                    section_name="Seminar",
                    section_code="SEM-2445",
                    expected_submission=20,
                    user_id=user.id
                )

            session.add(section1)
            session.commit()

            submission1 = Submissions(
                section_id=section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="john_stares_seminar.pptx",
                stored_filename="john_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/john_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission1)
            session.commit()


            submission2 = Submissions(
                section_id=section.id,
                uploader_name="Empress Stares",
                mat_no="DE.2018/5151",
                level=200,
                group="ACADEMY_NERD",
                original_filename="empress_stares_seminar.pptx",
                stored_filename="empress_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/empress_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission2)
            session.commit()

            submission3 = Submissions(
                section_id=section1.id,
                uploader_name="Ravivaa Stares",
                mat_no="DE.2018/3151",
                level=200,
                group="ACADEMY_NERD",
                original_filename="raviva_stares_seminar.pptx",
                stored_filename="raviva_stares_seminar.pptx",
                file_path=f"uploaded_files/{section1.section_name}/ravivastares_seminar.pptx",
                file_size=11141
            )

            session.add(submission3)
            session.commit()

            user = session.scalar(sql.select(User))

            assert user and section and submission3, submission1 and submission2 is not None

            session.delete(user)

            assert session.scalar(sql.select(User)) is None
            assert session.scalars(sql.select(Section).where(Section.user_id == user.id)).all() is None
            assert session.scalas(sql.select(Submissions).where(Submissions.section_id == section)).all() is None
            assert session.scalar(sql.select(Submissions).where(Submissions.section_id == section1)) is None


