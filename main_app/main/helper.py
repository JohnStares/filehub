from flask import current_app
from pathlib import Path
from main_app.extensions import db
from main_app.models import Submissions
import sqlalchemy as sql
import shutil
from typing import Sequence, Callable


def allowed_extension(filename: str) -> bool:
    """
    Returns the approved extentions

    :params:
        filename: A string: Name of the file that has an extension. eg. python_documentation.pdf
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["UPLOAD_EXTENSIONS"]


def save_uploaded_file(file, filename: str, section: str) -> Path:
    """
    This function is responsible for saving files to their respective directory

    :params:
        file: File object\n
        filename: Name of the file mostly gotten form secure_filname() function.\n
        section: The name of the section that will be used as a directory where the file will be saved
    """
    file_path = Path(current_app.config["UPLOAD_PATH"]) / section / filename

    try:
        # Create a directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        #Checks if the file already exist
        if file_path.exists():
            raise FileExistsError

        # Save the file
        file.save(file_path)

        return file_path
    
    except FileExistsError:
        raise FileExistsError
    except FileNotFoundError:
        raise FileNotFoundError
    except Exception as e:
        raise Exception
    

def bytes_converter(bytes: int) -> str:
    """
    Converts from bytes to either KB or MB

    :param:
        bytes: An integer in bytes
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1048576:
        return f"{bytes/1024:.1f} KB"
    else:
        return f"{bytes/1048576:.1f} MB"


def delete_multiple_files(section_id: int) -> None:
    """
    This function deletes all files that are submitted against a particular section in the database

    :params:
        section_id: An integer of the section that will be queried against the database

    :return:
        None
    """
    try:
        files = db.session.scalars(sql.select(Submissions).where(Submissions.section_id == section_id)).all()

        for file in files:
            db.session.delete(file)
        db.session.commit()

    except Exception:
        raise Exception
    

def delete_section_directory_and_its_files(section_name: str) -> bool:
    """
    This function deletes a directory in the uploaded_files and the files in that directory
    
    :params:
        section_name: A string: Name of the section

    :returns:
        bool
    """
    try:
        section_dir = Path(current_app.config["UPLOAD_PATH"]) / section_name

        if section_dir.exists() and section_dir.is_dir():
            shutil.rmtree(section_dir)

        return True
        
      
    except PermissionError:
        raise PermissionError
    except OSError:
        raise OSError
    except Exception:
        raise Exception
    
    
def number_of_submissions(section_id: int) -> Sequence[Submissions]:
    """
    Returns total number of objects related to that particular section

    :param:
        section_id: The section id
    """
    try:
        files = db.session.scalars(sql.select(Submissions).where(Submissions.section_id == section_id)).all()

        return files
    except Exception:
        raise Exception



def delete_file_from_directory(file_path: str) -> bool:
    """
    Deletes file in a particular directory.

    :param:
        file_path: A full path to that points to the file itself. eg. uploaded_file/Assignment/example.pdf or uploaded_files/example.pdf
    """
    try:
        path = Path(file_path)


        if path.exists() and path.is_file():
            path.unlink()

            return True
        
        raise FileNotFoundError
    
    except FileNotFoundError:
        return True
    except PermissionError:
        raise PermissionError
    except OSError:
        raise OSError
    except Exception:
        raise Exception
    


def get_percentage(expected_submission: int, section_id: int, func: Callable[[int], Sequence] = number_of_submissions) -> float | int:
    try:
        files = func(section_id)

        if files:
            number_of_files = len(files)

            percentage = number_of_files / expected_submission * 100

            return percentage
        
        return 0
    
    except Exception:
        raise Exception


def restore_path(file_path: str) -> None:
    path = Path(file_path)

    sub_dir = path.parent.name
    filename = path.name
    try:
        restored_path = Path(current_app.config["UPLOAD_PATH"]) / sub_dir / filename

        # Create a directory if it doesn't exist
        restored_path.parent.mkdir(parents=True, exist_ok=True)

    except Exception:
        raise Exception
