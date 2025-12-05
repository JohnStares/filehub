from flask import request, render_template, url_for, redirect, flash, send_file, abort
from flask_login import login_required, current_user
import sqlalchemy as sql
from werkzeug.utils import secure_filename
from flask import current_app
from pathlib import Path

from . import main_bp
from .forms import SectionForm, FileUpload
from main_app.models import Section, Submissions, User

from .helper import (
    allowed_extension, save_uploaded_file, bytes_converter, delete_multiple_files, 
    delete_section_directory_and_its_files, number_of_submissions, delete_file_from_directory,
    get_percentage, restore_path, reach_file_size
)

from main_app.extensions import db, limiter

import zipfile
import io


@main_bp.route("/")
def welcome():
    return render_template("main/welcome.html")


@main_bp.route("/home", methods=["GET"])
@limiter.limit("5 per minute")
@login_required
def home():
    try:
        current_app.logger.info("The home route is being accessed.")
        existing_sections = db.session.scalars(sql.select(Section).where(Section.user_id == current_user.id)).all()
        return render_template("main/home.html", sections=existing_sections, url_base=request.host_url.rstrip("/"), number_of_submissions=number_of_submissions, percentage=get_percentage)
    except Exception as e:
        flash("An unexpected error occured, we are handling it.")
        current_app.logger.error(f"Unexpected error occcured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.home"))



@main_bp.route("/create-section", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@login_required
def create_section():
    form = SectionForm()

    if request.method == "POST":
        try:
            current_app.logger.info(f"A post request is being made by {current_user.username} on create-section route")
            if form.validate_on_submit():
                section = Section(
                    user_id=current_user.id, section_name=form.section.data, 
                    section_code=form.section_code.data, 
                    expected_submission=form.expected_submission.data)
                
                db.session.add(section)
                db.session.commit()

                flash("Section created", "success")
                current_app.logger.info("A successful post request is made")
                return redirect(url_for("main_bp.home"))
            
            flash("Invalid form!", "warning")
            current_app.logger.warning(f"{current_user.username} made an invalid input on create-section route")
            return render_template("main/section.html", form=form)
        
        except Exception as e:
            db.session.rollback()
            flash("An error occured!", "error")
            current_app.logger.exception(f"An error occured due to {str(e)}", exc_info=True)
            return render_template("main/section.html", form=form)
    
    current_app.logger.info("The create-section route is being accessed")
    return render_template("main/section.html", form=form)


@main_bp.route("/upload-file/<username>/<section_name>", methods=["POST", "GET"])
@limiter.limit("10 per minute")
def upload_file(username, section_name):
    form = FileUpload()
    
    user = db.session.scalar(sql.select(User).where(User.username == username))
    section = db.session.scalar(sql.select(Section).where(Section.section_name == section_name))
    
    if request.method == "POST":
        try:

            if form.validate_on_submit():

                file = form.file.data

                if file.filename == "":
                    flash("Invalid file content", "error")
                    current_app.logger.warning(f"An empty filename was submitted")
                    return render_template("main/upload.html", form=form)
                
                # Check if file size is correct
                if not reach_file_size(file):
                    flash("File size should be between 10KB to 25MB")
                    return render_template("main/upload.html", form=form)


                # Secure the filename to prevent malicious attack in the server
                filename = secure_filename(file.filename)

                # Filter allowed extension
                if not allowed_extension(filename):
                    flash("Invalid file extention", "error")
                    current_app.logger.warning(f"File submitted have a wrong extension type")
                    return render_template("main/upload.html", form=form)


                # Save file to upload directory
                file_path = save_uploaded_file(file, filename, section_name)

                # Save other meta data and file_path to database
                submission = Submissions(
                    section_id=section.id, uploader_name=form.full_name.data,
                    mat_no=form.mat_no.data, level=form.level.data,
                    group=form.group.data, original_filename=filename,
                    stored_filename=filename, file_path=str(file_path),
                    file_size=file_path.stat().st_size, 
                )

                db.session.add(submission)
                db.session.commit()

                flash("File Uploaded Sucessfully", "success")
                current_app.logger.info(f"A successful file upload was made by {form.full_name.data}")
                return redirect(url_for("main_bp.upload_file", username=username, section_name=section_name))
            
            flash("Invalid data input", "error")
            current_app.logger.warning(f"An invalid input was made on this route. {form.errors}", exc_info=True)
            return render_template("main/upload.html", form=form)
        
        except FileExistsError:
            flash("The file exist, seems you have already uploaded the file", "error")
            current_app.logger.warning(f"A file with same details was being sent again by {form.full_name.data}", exc_info=True)
            return render_template("main/upload.html", form=form)
        
        except FileNotFoundError:
            flash("An error occured from us. Please try again", "warning")
            current_app.logger.error(f"Trying to save a file that doesn't exist. This needs a look", exc_info=True)
            return render_template("main/upload.html", form=form)
        
        except Exception as e:
            db.session.rollback()

            # Ensures that the file is deleted from the directory if the database fails to save to avoid oprhan storage.
            path_to_file = Path(current_app.config["UPLOAD_PATH"]) / section_name / filename
            delete_file_from_directory(path_to_file)

            flash("Internal server down", "warning")
            current_app.logger.exception(f"An error occured due to {str(e)}", exc_info=True)
            return render_template("main/upload.html", form=form)

    if user and section:
        current_app.logger.info("Upload file route is being accessed")
        return render_template("main/upload.html", form=form)
    
    current_app.logger.warning("A wrong url was tried on this route")
    abort(404)



@main_bp.route("/delete-section/<section_id>", methods=["POST"])
@limiter.limit("5 per minute")
@login_required
def delete_section(section_id):
    try:
        section = db.session.scalar(sql.select(Section).where(
            (Section.user_id == current_user.id) &
            (Section.id == section_id)
        ))


        if section:
            if delete_section_directory_and_its_files(section.section_name):
                delete_multiple_files(section_id)
                db.session.delete(section)
                db.session.commit()

                flash("Section deleted successfully", "success")
                current_app.logger.info("A section was successfully deleted")
                return redirect(url_for("main_bp.home"))
        
        flash("Unauthorized", "warning")
        current_app.logger.warning(f"Unathorized delete attempt by {current_user.username} on section {section_id}")
        return abort(403)
    
    except PermissionError as p:
        flash("Permission Error", "warning")
        current_app.logger.warning(f"Permission was denied while trying to delete a section due to {str(p)}", exc_info=True)
        return redirect(url_for("main_bp.home"))
    
    except OSError as o:
        flash("OS Error", "warning")
        current_app.logger.error(f"OSError ecountered due to {str(o)}", exc_info=True)
        return redirect(url_for("main_bp.home"))

        
    except Exception as e:
        flash("Internal Error", "warning")
        db.session.rollback()
        current_app.logger.exception(f"An unexpected error occured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.home"))



@main_bp.route("/view-files/<section_id>", methods=["GET"])
@limiter.limit("5 per minute")
@login_required
def view_files(section_id):
    try:
        section = db.session.scalar(sql.select(Section).where(
            (Section.user_id == current_user.id) &
            (Section.id == section_id)
        ))

        if not section:
            flash("You are not authorized to view that section", "error")
            current_app.logger.warning(f"Unathorized view attempt by {current_user.username} on section {section_id}")
            return abort(403)

        page = request.args.get("page", 1, type=int)

        query = sql.select(Submissions).where(Submissions.section_id == section_id)
        files = db.paginate(query, page=page, per_page=current_app.config["FILES_PER_PAGE"], error_out=False)

        next_url = url_for("main_bp.view_files", section_id=section_id, page=files.next_num) \
            if files.has_next else None
        
        prev_url = url_for("main_bp.view_files", section_id=section_id, page=files.prev_num) \
            if files.has_prev else None
        

        current_app.logger.info("View-files routes was accessed")
        return render_template("main/view-file.html", files=files, bytes_converter=bytes_converter, next=next_url, prev=prev_url)
    
    
    except Exception as e:
        flash("An error occured! Please try again", "warning")
        current_app.logger.error(f"An unexpected error occcured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.home"))




@main_bp.route("/download-files/<section_id>/<section_name>", methods=["GET"])
@limiter.limit("5 per minute")
@login_required
def download_files(section_id: str, section_name: str):
    try:
        files = db.session.scalars(
            sql.select(Submissions).join(Submissions.section).where(
                (Submissions.section_id == section_id) &
                (Section.user_id == current_user.id)
            )
        ).all()

        if not files or files is None:
            flash("No files in this category to download", "warning")
            return redirect(url_for("main_bp.home"))

        # create ZIP in memory
        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = file.file_path

                new_filename = f"{file.uploader_name}_{file.mat_no}_{file.original_filename}"

                zipf.write(file_path, arcname=new_filename)


        memory_file.seek(0)

        flash("Downloading files", "success")
        current_app.logger.info("Downloading files in progress")
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{section_name}.zip"
        )
    
    except FileNotFoundError:
        flash("Coulnd't find some files", "error")
        current_app.logger.warning("A file couldn't download due to it missing", exc_info=True)
        return redirect(url_for("main_bp.home"))
    
    except Exception as e:
        flash("Internal Service issue", "error")
        current_app.logger.exception(f"An unexpected error occured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.home"))



@main_bp.route("/delete-file/<int:file_id>", methods=["POST"])
@limiter.limit("5 per minute")
@login_required
def delete_file(file_id: int):
    try:
        file = db.session.scalar(sql.select(Submissions).join(Submissions.section).where(Submissions.id == file_id))


        if file:
            if file.section.user_id != current_user.id:
                flash("Unathorized attempt", "error")
                current_app.logger.warning(f"Unathorized delete attempt by {current_user.username} on File {file_id}")
                abort(403)

            if delete_file_from_directory(file.file_path):
                db.session.delete(file)
                db.session.commit()

                flash("File deleted successfully", "success")
                current_app.logger.info(f"{current_user.username} successfully deleted a file")
                return redirect(url_for("main_bp.view_files", section_id=file.section_id))
        
        flash("File not found", "warning")
        current_app.logger.warning("File not found in an attempt to delete it.")
        return redirect(url_for("main_bp.view_files", section_id=file.section_id))

    except PermissionError:
        flash("Permission Denied", "error")
        current_app.logger.warning(f"{current_user.username} was denied permission while trying to delete a file", exc_info=True)
        return redirect(url_for("main_bp.view_files", section_id=file.section_id))
    except OSError:
        flash("Having probelm deleting file", "error")
        current_app.logger.warning(f"OSError encountered while trying to delete a file", exc_info=True)
        return redirect(url_for("main_bp.view_files", section_id=file.section_id))
    except Exception as e:
        db.session.rollback()
        flash("Internal server error", "error")
        current_app.logger.exception(f"An error occured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.view_files", section_id=file.section_id))
    


@main_bp.route("/delete-files/<int:section_id>", methods=["POST"])
@limiter.limit("5 per minute")
@login_required
def delete_files(section_id: int):
    try:
        section = db.session.scalar(sql.select(Section).where(Section.id == section_id))
        
        if not section:
            flash("invalid attempt. Doesn't exist", "error")
            return redirect(url_for("main_bp.home"))
        
        if section.user_id != current_user.id:
            flash("Unathorized attempt", "warning")
            current_app.logger.warning(f"Unathorized delete attempt by {current_user.username} on a file tied to section {section_id}")
            abort(403)
            
        files = db.session.scalars(sql.select(Submissions).where(Submissions.section_id == section_id)).all()

        if not files:
            flash("No files to delete", "warning")
            current_app.logger.warning("File not found in an attempt to delete it.")
            return redirect(url_for("main_bp.home"))
        
        deleted_file_path = [] # Keeps track of files_paths that couldn't be deleted

        for file in files:
            if delete_file_from_directory(file.file_path):
                deleted_file_path.append(file.file_path)
                db.session.delete(file)
            else:
                for path in deleted_file_path:
                    restore_path(path)
                    raise OSError

        db.session.commit()


        flash("All files deleted", "success")
        current_app.logger.info(f"{current_user.username} successfully deleted multiple files")
        return redirect(url_for("main_bp.home"))
        

    except PermissionError:
        db.session.rollback()
        flash("Permission Denied", "error")
        current_app.logger.warning(f"{current_user.username} was denied permission while trying to delete a file", exc_info=True)
        return redirect(url_for("main_bp.home"))
    except OSError:
        db.session.rollback()
        flash("Having probelm deleting file", "error")
        current_app.logger.warning(f"OSError encountered while trying to delete a file", exc_info=True)
        return redirect(url_for("main_bp.home"))
    except Exception as e:
        db.session.rollback()
        flash("Internal server error", "error")
        current_app.logger.exception(f"An error occured due to {str(e)}", exc_info=True)
        return redirect(url_for("main_bp.home"))

