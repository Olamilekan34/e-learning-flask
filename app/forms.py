from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from flask_login import current_user
from app.models import Course
from flask_wtf.file import FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student', 'Student'), ('educator', 'educator')])
    submit = SubmitField('Register')

class StudentForm(FlaskForm):
    sur_name = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    image = FileField('Profile Image')

class InstructorForm(FlaskForm):
    instructor_sur_name = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    instructor_first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(min=2, max=100)])
    facebook = StringField('Facebook', validators=[Length(max=100)])
    linkedin = StringField('LinkedIn', validators=[Length(max=100)])
    twitter = StringField('Twitter', validators=[Length(max=100)])
    instructor_image = FileField('Profile Image')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
class UpdateInstructorProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional()])
    sur_name = StringField('Surname', validators=[Optional()])
    image = FileField('Profile Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    facebook = StringField('Facebook', validators=[Optional()])
    linkedin = StringField('LinkedIn', validators=[Optional()])
    twitter = StringField('Twitter', validators=[Optional()])
    specialization = StringField('Specialization', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Update Profile')

class UpdateStudentProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional()])
    sur_name = StringField('Surname', validators=[Optional()])
    image = FileField('Profile Image', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'])])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    submit = SubmitField('Update Profile')
    
class CourseForm(FlaskForm):
    code = StringField('Course Code', validators=[DataRequired()])
    title = StringField('Course Title', validators=[DataRequired()])
    unit = StringField('Course Unit', validators=[DataRequired()])
    semester = StringField('Course Semester', validators=[DataRequired()])
    level = StringField('Course Level', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Course')
    image = FileField('Profile Image')
    session = StringField('Course Code', validators=[DataRequired()])

class LearningMaterialForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    file = FileField('Upload Material', validators=[FileRequired(), FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'], 'Documents only!')])
    submit = SubmitField('Add Material')


class DiscussionRoomForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    
class QuizForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    options = TextAreaField('Options (comma separated)', validators=[DataRequired()])
    answer = StringField('Correct Answer', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Quiz')

    def __init__(self, *args, **kwargs):
        super(QuizForm, self).__init__(*args, **kwargs)
        # Populate course choices for instructors
        if current_user.is_authenticated and current_user.role == 'instructor':
            self.course_id.choices = [
                (c.id, c.title) for c in Course.query.filter_by(instructor_id=current_user.id).all()
            ]