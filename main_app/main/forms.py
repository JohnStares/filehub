from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileRequired, FileSize


class SectionForm(FlaskForm):
    section = StringField("Section name", validators=[DataRequired()], render_kw={"placeholder": "eg. midterm project"})
    section_code = StringField("Section Code", render_kw={"placeholder": "e.g LECT-2867"})
    expected_submission = IntegerField("Expected Submissions", validators=[Optional()])

    submit = SubmitField("Create")



class FileUpload(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()], render_kw={"placeholder": "John Stares"})
    mat_no = StringField("Mat No", validators=[Optional()], render_kw={"placeholder": "DE.2025/5713"})
    level = StringField("Level", validators=[Optional()], render_kw={"placeholder": "300"})
    group = StringField("Group", validators=[Optional()], render_kw={"placeholder": "Group you belong to"})
    file = FileField("File", validators=[FileRequired(), FileSize(max_size=25*1024*1024, min_size=10 * 1024, message="File must be between 10K and 25MB")])

    submit = SubmitField("Upload")


