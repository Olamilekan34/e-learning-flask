from app import db  # Import Bcrypt from your app
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

# # User model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     role = db.Column(db.String(50))  # Admin, Instructor, Student

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    role = db.Column(db.String(20))  # 'admin', 'instructor', 'student'
    # Relationships
    # courses = db.relationship('Course', backref='user_courses', lazy=True)
    # enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    # Password handling with Bcrypt
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Educator(User):
    __tablename__ = 'educators'
    # id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    first_name = db.Column(db.String(50))  # Add first name
    sur_name = db.Column(db.String(50)) 
    
    specialization = db.Column(db.String(100))  # Field specific to educators
    facebook = db.Column(db.String(100))  # Educator's Facebook link
    linkedin = db.Column(db.String(100))  # Educator's LinkedIn link
    twitter = db.Column(db.String(100))  # Educator's Twitter link
    image = db.Column(db.String(100))  # Educator's image link
    # Relationships
    # courses = db.relationship('Course', backref='educator_courses', lazy=True)
    # educator_courses = db.relationship('Course', backref='educator', overlaps="courses,educator")
    educator_courses = db.relationship('Course', back_populates='instructor', lazy=True)

class Student(User):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    first_name = db.Column(db.String(50))  # Student's first name
    sur_name = db.Column(db.String(50))  # Student's surname
    gender = db.Column(db.String(7)) 
    enrollment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date of enrollment
    # major = db.Column(db.String(100))  # Student's major or field of study
    image = db.Column(db.String(100))  # Path to the student's profile image
    # facebook = db.Column(db.String(100))  # Student's Facebook link
    # linkedin = db.Column(db.String(100))  # Student's LinkedIn link
    # twitter = db.Column(db.String(100))  # Student's Twitter link

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student_enrollments', lazy=True)
    progress = db.relationship('Progress', backref='student_progress', lazy=True)
    gamification = db.relationship('Gamification', backref='student_gamification', lazy=True)
    
# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(100))
    instructor_id = db.Column(db.Integer, db.ForeignKey('educators.id'))
    enrollments = db.relationship('Enrollment', back_populates='course', lazy=True)
    # enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    quizzes = db.relationship('Quiz', backref='course', lazy=True)
    # instructor = db.relationship('Educator', backref=db.backref('educator_courses', lazy=True))
    # instructor = db.relationship('Educator', backref='courses', overlaps="courses,educator")
    instructor = db.relationship('Educator', back_populates='educator_courses', lazy=True)
    session = db.Column(db.String(100), nullable=False)
    discussion_rooms = db.relationship('DiscussionRoom', backref='course', lazy=True)
    learning_materials = db.relationship('LearningMaterial', back_populates='course', lazy=True)


class LearningMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(200))  # path or filename of uploaded material
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    course = db.relationship('Course', back_populates='learning_materials')

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', back_populates='enrollments', lazy=True)
    enrollment_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    
    
# Progress model
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    progress = db.Column(db.Float)  # Percentage of completion

class Gamification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Integer, default=0)
    badges = db.Column(db.JSON, default=[])  # e.g., ["python_beginner", "quiz_master"]
    level = db.Column(db.Integer, default=1)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200))
    options = db.Column(db.JSON)  # ["Option1", "Option2", ...]
    answer = db.Column(db.String(100))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

# # Badge Model
# class Badge(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     description = db.Column(db.Text)

# class Points(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     points = db.Column(db.Integer, default=0)

#     user = db.relationship('User', backref=db.backref('points', lazy=True))

class DiscussionRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    # course = db.relationship('Course', backref=db.backref('discussion_rooms', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('discussion_room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(64))
    content = db.Column(db.Text)
    role = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_id = db.Column(db.String(50))  # For matching frontend IDs
    status = db.Column(db.String(10))  # 'correct' or 'incorrect'

    def to_dict(self):
        return {
            'reply_id': self.reply_id,
            'username': self.username,
            'reply': self.content,
            'timestamp': self.timestamp.strftime("%d %b %Y, %I:%M %p"),
            'role': self.role,
            'status': self.status
        }