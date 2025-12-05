import pytest
from main_app import create_app
from main_app.extensions import db
from main_app.models import User, Section, Submissions


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")

    yield app


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def session(app):
    with app.app_context():

        db.drop_all()
        db.create_all()

        yield db.session

        db.session.remove()
        db.drop_all()



@pytest.fixture(scope="function")
def sample_user(app, session):
    with app.app_context():
        user = User(
            username="John_Stares",
            email="john@gmail.com"
        )

        user.hash_password("john123456")
        session.add(user)
        session.commit()
        session.expire_all()

        yield user



@pytest.fixture(scope="function")
def sample_section(app, session, sample_user):
    with app.app_context():
        section = Section(
            section_name="Assignment",
            section_code="ASS-2445",
            expected_submission=10,
            user_id=sample_user.id
        )

        session.add(section)
        session.commit()
        session.expire_all()

        yield section



@pytest.fixture(scope="function")
def sample_submission(app, session, sample_section):
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
        session.expire_all()


        yield submission