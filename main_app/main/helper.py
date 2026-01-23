from flask import current_app
from pathlib import Path
from main_app.extensions import db
from main_app.models import Submissions, Section
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
    """
    Restores a file back to it's path
    
    :param file_path: A file path
    :type file_path: str
    """
    path = Path(file_path)

    sub_dir = path.parent.name
    filename = path.name
    try:
        restored_path = Path(current_app.config["UPLOAD_PATH"]) / sub_dir / filename

        # Create a directory if it doesn't exist
        restored_path.parent.mkdir(parents=True, exist_ok=True)

    except Exception:
        raise Exception


def duplicate_submission(*, name: str | None = None, mat_no: str | None = None, section_obj: Section) -> bool:
    """
    Prevent duplicate upload of files by same on a section either by name or mat_no. Keyword argument is required on your choice.
    
    :param name: Uploader's name
    :type name: str | None
    :param mat_no: Uploader's mat-no
    :type mat_no: str | None
    :param section_obj: Database objection of where the uploads are made
    :type section_obj: Section
    :return: True if duplicate otherwise false
    :rtype: bool
    """
    uploader_details = section_obj.submissions

    if name:
        if not isinstance(name, str):
            try:
                name = str(name)
            except ValueError:
                raise

        for uploader_name in uploader_details:
            if uploader_name.uploader_name == name:
                return True
        
        return False
    
    if not isinstance(mat_no, str):
        try:
            mat_no = str(mat_no)
        except ValueError:
            raise

    for uploader_mat_no in uploader_details:
        if uploader_mat_no.mat_no == mat_no:
            return True
        
    return False


def get_file_extension(file_path: str) -> str:
    """
    Returns the extension of a file
    
    :param file_path: File path leading to the file
    :type file_path: str
    :return: Description
    :rtype: str
    """
    if not isinstance(file_path, str):
        try:
            file_path = str(file_path)
        except ValueError:
            raise

    extension = file_path.split(".")
    
    return extension[1]


def special_alphanum() -> str:
    """
    Generates alphabets, numbers and few special characters
    
    :return: A string of alphabets, numbers and few special characters
    :rtype: str
    """
    from string import ascii_letters, digits

    return ascii_letters + digits + ".-_"



def username_to_gibberish(username: str, key: int = 10) -> str:
    """
    This takes a username and returns a gibberish version that using key as a mixer
    
    :param username: The username you want to convert
    :type username: str
    :param key: A key that is used to cipher how the gibberish will be produced
    :type key: int
    :return: Returns gibberish
    :rtype: str
    """
    list_of_special_alphanum = special_alphanum()
    len_list_of_special_alphanum = len(list_of_special_alphanum)
    char_to_index = {char: idx for idx, char in enumerate(list_of_special_alphanum)}

    gibberish = []

    key = key % len_list_of_special_alphanum
    
    for char in username:
        if char not in char_to_index:
            if char == "'":
                gibberish.append("~")
                continue
            else:
                gibberish.append(char)
                continue
        
        idx = char_to_index[char]
        new_idx = (key + idx) % len_list_of_special_alphanum
        gibberish.append(list_of_special_alphanum[new_idx])
        
    return "".join(gibberish)


def gibberish_to_username(gibberish: str, key: int = 10) -> str:
    """
    Takes in a gibberish it ealier converted using the username_to_gibberish function and returns a username
    
    :param gibberish: The gibberish version of a username
    :type gibberish: str
    :param key: The key used in converting it to a gibberish
    :type key: int
    :return: Returns a username
    :rtype: str
    """
    list_of_special_alphanum = special_alphanum()
    len_list_of_special_alphanum = len(list_of_special_alphanum)
    char_to_index = {char: idx for idx, char in enumerate(list_of_special_alphanum)}

    username = []

    key = key % len_list_of_special_alphanum
    
    for char in gibberish:
        if char not in char_to_index:
            if char == "~":
                username.append("'")
                continue
            else:
                username.append(char)
                continue

        idx = char_to_index[char]
        new_idx = (idx - key) % len_list_of_special_alphanum

        username.append(list_of_special_alphanum[new_idx])

    return "".join(username)