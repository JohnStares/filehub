import pytest
from main_app.models import User, Section, Submissions
import sqlalchemy as sql
import time


class TestUnprotectedRoutes:
    def test_welcome_page(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert b'FileHub' in response.data
        assert b'Sign In' and b'Sign Up' in response.data
        assert b"What is FileHub" in response.data


    def test_sign_up_page(self, client):
        response = client.get("auth/sign-up")

        assert response.status_code == 200
        assert b"Sign Up" in response.data
        assert b"Already have an account?" in response.data
        assert b"Sign In" not in response.data


    def test_sign_in_page(self, client):
        response = client.get("auth/sign-in")

        assert response.status_code == 200
        assert b"Sign In" in response.data
        assert b'Don\'t have an account?' in response.data

    
    def test_upload_files_page(self, app, session, client):
        with app.app_context():
            user = User(
                username="King_Rez",
                email="kingrez@gmail.com",
            )
            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Project",
                section_code="PRO-7623",
                expected_submission=10,
                user_id=user.id
            )
            session.add(section)
            session.commit()

            assert user is not None
            assert section is not None

            response1 = client.get(f"upload-file/{user.username}/{section.section_name}")

            assert response1.status_code == 200
            assert b"Upload File" in response1.data
            assert b'Upload' in response1.data

            response2 = client.get("upload-file/testuser/section")

            assert response2.status_code == 404



class TestProtectedRoutes:
    """This test that a protected route will always redirect to the login page if the user is not authenticated"""
    
    def test_homepage(self, client):
        response = client.get("/home", follow_redirects=False)

        assert response.status_code == 302
        assert "/sign-in" in response.location


    def test_create_section_route(self, client):
        response = client.get("/create-section", follow_redirects=False)

        assert response.status_code == 302
        assert "/sign-in" in response.location


    def test_delete_section(self, app, session, client):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
            )

            session.add(section)
            session.commit()

            response = client.post(f"/delete-section/{section.id}", follow_redirects=False)

            assert response.status_code == 302
            assert "sign-in" in response.location


    
    def test_view_files(self, app, session, client):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
            )

            session.add(section)
            session.commit()


            response = client.get(f"/view-files/{section.id}", follow_redirects=False)

            assert response.status_code == 302
            assert "sign-in" in response.location



    def test_download_files(self, app, session, client):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
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

            response = client.get(f"/download-files/{section.id}/{section.section_name}", follow_redirects=False)

            assert response.status_code == 302
            assert "sign-in" in response.location


    
    def test_delete_file(self, app, session, client):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
            )

            session.add(section)
            session.commit()

            submission = Submissions(
                section_id=section.id,
                uploader_name="John Stares",
                mat_no="DE.2018/5161",
                level=200,
                group="ACADEMY_NERD",
                original_filename="empress_stares_seminar.pptx",
                stored_filename="empress_stares_seminar.pptx",
                file_path=f"uploaded_files/{section.section_name}/empress_stares_seminar.pptx",
                file_size=11141
            )

            session.add(submission)
            session.commit()

            response = client.post(f"/delete-file/{submission.id}", follow_redirects=False)

            assert response.status_code == 302
            assert "sign-in" in response.location



    def test_delete_files(self, app, session, client):
        with app.app_context():
            user = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user.hash_password("john123456")
            session.add(user)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
            )

            session.add(section)
            session.commit()

            response = client.post(f"/delete-files/{section.id}", follow_redirects=False)

            assert response.status_code == 302
            assert "sign-in" in response.location





class TestAuthenticatedRoutes:
    """This class test authentication in routes that requires users to be log or be logged in"""

    def test_homepage_when_logged_in(self, app, sample_user, client):
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            response = client.get("/home")

            assert response.status_code == 200
            assert b'Welcome back!' in response.data
            assert b'Active Sections' in response.data


    def test_create_section_route_get_when_logged_in(self, app, sample_user, client):
        """This gets the create_section page when the user is logged in"""
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            response = client.get("/create-section")

            assert response.status_code == 200
            assert b'Create Section' in response.data


        
    def test_create_section_route_post_when_logged_in(self, app, session, sample_user, client):
        """This sends a post request on the create-section route when the user is logged in"""
        time.sleep(60)
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            response = client.post(
                "/create-section",
                data={
                    "section": "Python Tutorial",
                    "section_code": "PYTT-3435",
                    "expected_submission": 15
                }
            )

            section = session.scalar(sql.select(Section).where(Section.section_name =="Python Tutorial"))

            assert section is not None
            assert section.expected_submission == 15


        
    def test_view_files_route_get_when_logged_in(self, app, sample_user, sample_section, client):
        """This gets the view files route when the user is logged in"""
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            response = client.get(f"/view-files/{sample_section.id}")

            assert response.status_code == 200
            assert b'View All Files' in response.data


    def test_delete_section_when_logged_in(self, app, session, sample_user, sample_section, client):
        """This test deleting of section when logged in"""
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            response = client.post(f"/delete-section/{sample_section.id}")

            assert response.status_code == 302 # I redirects to the homepage after the delete request is made

            section = session.scalar(sql.select(Section).where(Section.id == sample_section.id))

            assert section is None



    def test_delete_files_when_logged_in(self, app, session, sample_user, sample_section, sample_submission, client):
        time.sleep(60)
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            assert session.scalar(sql.select(Submissions).where(Submissions.id == sample_submission.id)) is not None

            response = client.post(f"/delete-files/{sample_section.id}")

            assert response.status_code == 302

            assert session.scalar(sql.select(Submissions).where(Submissions.id == sample_submission.id)) is None



    def test_delete_file_when_logged_in(self, app, session, sample_user, sample_submission, client):
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            assert session.scalar(sql.select(Submissions).where(Submissions.id == sample_submission.id)) is not None

            response = client.post(f"/delete-file/{sample_submission.id}")

            assert response.status_code == 302
            assert session.scalar(sql.select(Submissions).where(Submissions.id == sample_submission.id)) is None


    
    def test_logout_when_logged_in(self, app, sample_user, client):
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            home_response = client.get("/home")
            assert b'Welcome back!' in home_response.data

            log_out_response = client.post('/auth/logout')

            assert log_out_response.status_code == 302
            assert "/sign-in" in log_out_response.location

            response = client.get("/home", follow_redirects=False)

            assert response.status_code == 302
            assert "/sign-in" in response.location





class TestUploadAndDownloadRoutes:
    """This will test upload and download functionalities"""
    def test_uploading_of_files_when_logged_in(self, app, session, sample_user, sample_section, client):
        with app.app_context():
            client.post(
                "/auth/sign-in",
                data={
                    "username": f"{sample_user.username}",
                    "password": "john123456"
                }
            )

            assert session.scalar(sql.select(Submissions).where(Submissions.uploader_name == "King Rez")) is None

            from io import BytesIO

            content = b'This is just a sample of the file for testing1'
            response = client.post(
                f"upload-file/{sample_user.username}/{sample_section.section_name}",
                data={
                    "full_name": "King Rez",
                    "mat_no": "DE.2018/4178",
                    "level": 300,
                    "group": "AEB NERD",
                    "file": (BytesIO(content), 'tests.docx')
                },
                content_type="multipart/form-data",
                follow_redirects=True
            )

            assert response.status_code == 200
            assert session.scalar(sql.select(Submissions).where(Submissions.uploader_name == "King Rez")) is not None

            client.get(f"/delete-section/{sample_section.id}")


    
    def test_uploading_of_files_when_not_logged_in(self, app, session, sample_user, sample_section, client):
        with app.app_context():
            assert session.scalar(sql.select(Submissions).where(Submissions.uploader_name == "Justice Stares")) is None

            from io import BytesIO

            response = client.post(
                f"upload-file/{sample_user.username}/{sample_section.section_name}",
                data={
                    "full_name": "Justice Stares",
                    "mat_no": "DE.2018/4178",
                    "level": 300,
                    "file": (BytesIO(b'This is just a sample of file for testing2. Testing, Testing, Testing'), "test1.odt")
                },
                content_type="multipart/form-data",
                follow_redirects=True
            )

            assert response.status_code == 200
            assert session.scalar(sql.select(Submissions).where(Submissions.uploader_name == "Justice Stares")) is not None

            client.get(f"/delete-section/{sample_section.id}")



    
    def test_downloading_of_files_when_logged_in(self, app, session, sample_user, sample_section, client):
        with app.app_context():
            from io import BytesIO

            response1 = client.post(
                f"upload-file/{sample_user.username}/{sample_section.section_name}",
                data={
                    "full_name": "Empress Stares",
                    "mat_no": "DE.2018/4178",
                    "level": 300,
                    "file": (BytesIO(b'Testing! This is just a sample of file for testing3'), "test3.txt")
                },
                content_type="multipart/form-data",
                follow_redirects=True
            )

            assert response1.status_code == 200

            response2 = client.post(
                f"upload-file/{sample_user.username}/{sample_section.section_name}",
                data={
                    "full_name": "Raviva Stares",
                    "mat_no": "DE.2018/4178",
                    "level": 300,
                    "file": (BytesIO(b'Sample! Testing! This is just a sample of file for testing4'), "test4.doc")
                },
                content_type="multipart/form-data",
                follow_redirects=True
            )

            assert response2.status_code == 200

            files = session.scalars(sql.select(Submissions).where(Submissions.section_id == sample_section.id)).all()

            assert len(files) == 2


            response3 = client.get(f"download-files/{sample_section.id}/{sample_section.section_name}")

            assert response3.status_code == 302

            client.get(f"/delete-section/{sample_section.id}")



class TestAuthorization:
    """This test what a user is not allowed to do"""

    def test_if_user_cannot_view_another_user_files(self, app, session, client):
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

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user.id
            )

            session.add(section)
            session.commit()


            client.post(
                "/auth/sign-in",
                data={
                    "username": "Raviva_Stares",
                    "password": "john123456"
                }
            )


            response = client.get(f"/view-files/{section.id}")

            assert response.status_code in [401, 302, 404, 403]



    def test_if_user_can_delete_another_user_section(self, app, session, client):
        with app.app_context():
            user1 = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user1.hash_password("john123456")
            session.add(user1)
            session.commit()

            user2 = User(
                username="Raviva_Stares",
                email="raviva@gmail.com"
            )

            user2.hash_password("john123456")
            session.add(user2)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user1.id
            )

            session.add(section)
            session.commit()


            client.post(
                "/auth/sign-in",
                data={
                    "username": "Raviva_Stares",
                    "password": "john123456"
                }
            )

            response = client.post(f"delete-section/{section.id}")

            assert response.status_code == 302


    def test_if_user_can_delete_another_user_files(self, app, session, client):
        with app.app_context():
            user1 = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user1.hash_password("john123456")
            session.add(user1)
            session.commit()

            user2 = User(
                username="Raviva_Stares",
                email="raviva@gmail.com"
            )

            user2.hash_password("john123456")
            session.add(user2)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user1.id
            )

            session.add(section)
            session.commit()


            client.post(
                "/auth/sign-in",
                data={
                    "username": "Raviva_Stares",
                    "password": "john123456"
                }
            )

            response = client.post(f"delete-files/{section.id}")

            assert response.status_code == 302



    def test_if_user_can_delete_another_user_file(self, app, session, client):
        with app.app_context():
            user1 = User(
                username="Empress_Stares",
                email="empress@gmail.com"
            )

            user1.hash_password("john123456")
            session.add(user1)
            session.commit()

            user2 = User(
                username="Raviva_Stares",
                email="raviva@gmail.com"
            )

            user2.hash_password("john123456")
            session.add(user2)
            session.commit()

            section = Section(
                section_name="Seminar",
                section_code="SEM-2445",
                expected_submission=10,
                user_id=user1.id
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


            client.post(
                "/auth/sign-in",
                data={
                    "username": "Raviva_Stares",
                    "password": "john123456"
                }
            )

            response = client.post(f"delete-files/{submission.id}")

            assert response.status_code == 302
