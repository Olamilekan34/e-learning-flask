# routes.py
from datetime import datetime
from flask_socketio import SocketIO, send

from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt, socketio, login_manager
from flask import current_app as app
from app.models import DiscussionRoom, Message, User, Student, Educator, Course, Enrollment, Quiz, Gamification, LearningMaterial
from app.forms import ChangePasswordForm, LoginForm, RegistrationForm, StudentForm, InstructorForm, CourseForm, QuizForm, DiscussionRoomForm, UpdateInstructorProfileForm, UpdateStudentProfileForm, LearningMaterialForm
from functools import wraps
import os
from werkzeug.utils import secure_filename
# from flask_login import LoginManager

# login_manager = LoginManager()
main_bp = Blueprint('main_bp', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, name_prefix):
    if file and allowed_file(file.filename):
        safe_filename = secure_filename(file.filename)
        filename = f"{name_prefix}_{safe_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            return filename
        except Exception as e:
            flash(f"Failed to save the file: {e}", "danger")
            return None
    flash("Invalid file type. Please upload a valid image.", "danger")
    return None

# Helper to check roles
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("You don't have permission to access this page.", "danger")
                return redirect(url_for('main_bp.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@main_bp.route('/')
def home():
    educators = Educator.query.limit(4).all()
    courses = Course.query.all()
    top_users = Gamification.query.join(User).order_by(Gamification.points.desc()).limit(5).all()
    return render_template('home.html', courses=courses, top_users=top_users, educators=educators)

# Authentication Routes
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You have already login', 'danger')
        return redirect(url_for('main_bp.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):  # Check hashed password
            login_user(user)
            return redirect(url_for('main_bp.home'))
        else:
            form.email.errors.append("Invalid email or password")
            # flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

# @main_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         flash('You are already logged in.', 'danger')
#         return redirect(url_for('main_bp.home'))

#     form = RegistrationForm()
#     student_form = StudentForm(request.form)
#     instructor_form = InstructorForm(request.form)
    

#     if form.validate_on_submit():
#         role = form.role.data
#         try:
#             # Role-specific handling
#             if role == 'student' and student_form.validate():
#                 file = request.files.get('image')
#                 filename = save_image(file, f"{student_form.sur_name.data}_{student_form.first_name.data}")
#                 if file and not filename:
#                     return redirect(request.url)

#                 student = Student(
#                     username=form.username.data,
#                     email=form.email.data,
#                     role=role,
#                     sur_name=student_form.sur_name.data,
#                     first_name=student_form.first_name.data,
#                     gender=student_form.gender.data,
#                     image=filename
#                 )
#                 student.password = form.password.data
#                 db.session.add(student)

#             elif role == 'educator' and instructor_form.validate():
#                 file = request.files.get('instructor_image')
#                 filename = save_image(file, f"{instructor_form.instructor_sur_name.data}_{instructor_form.instructor_first_name.data}")
#                 if file and not filename:
#                     return redirect(request.url)

#                 instructor = Educator(
#                     username=form.username.data,
#                     email=form.email.data,
#                     role=role,
#                     sur_name=instructor_form.instructor_sur_name.data,
#                     first_name=instructor_form.instructor_first_name.data,
#                     specialization=instructor_form.specialization.data,
#                     facebook=instructor_form.facebook.data,
#                     linkedin=instructor_form.linkedin.data,
#                     twitter=instructor_form.twitter.data,
#                     image=filename
#                 )
#                 instructor.password = form.password.data
#                 db.session.add(instructor)
#             else:
#                 flash('Invalid form submission for the selected role.', 'danger')
#                 return render_template('register.html', form=form, student_form=student_form, instructor_form=instructor_form)

#             db.session.commit()
#             flash('Registration successful! Please log in.', 'success')
#             return redirect(url_for('main_bp.login'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f"An error occurred: {str(e)}", 'danger')
#             return redirect(request.url)
#     return render_template('register.html', form=form, student_form=student_form, instructor_form=instructor_form)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'danger')
        return redirect(url_for('main_bp.home'))

    form = RegistrationForm()
    student_form = StudentForm()
    instructor_form = InstructorForm()

    if request.method == 'POST':
        form = RegistrationForm(request.form)
        student_form = StudentForm(request.form)
        instructor_form = InstructorForm(request.form)
        role = form.role.data

        form_valid = form.validate()
        student_valid = student_form.validate()
        instructor_valid = instructor_form.validate()

        if form_valid and (
            (role == 'student' and student_valid) or
            (role == 'educator' and instructor_valid)
        ):
            try:
                # Handle file upload and data saving for student
                if role == 'student':
                    file = request.files.get('image')
                    filename = save_image(file, f"{student_form.sur_name.data}_{student_form.first_name.data}")
                    if file and not filename:
                        flash("Invalid image upload", 'danger')
                        return redirect(request.url)

                    student = Student(
                        username=form.username.data,
                        email=form.email.data,
                        role='student',
                        sur_name=student_form.sur_name.data,
                        first_name=student_form.first_name.data,
                        gender=student_form.gender.data,
                        image=filename
                    )
                    student.password = form.password.data
                    db.session.add(student)

                # Handle file upload and data saving for educator
                elif role == 'educator':
                    file = request.files.get('instructor_image')
                    filename = save_image(file, f"{instructor_form.instructor_sur_name.data}_{instructor_form.instructor_first_name.data}")
                    if file and not filename:
                        flash("Invalid image upload", 'danger')
                        return redirect(request.url)

                    educator = Educator(
                        username=form.username.data,
                        email=form.email.data,
                        role='educator',
                        sur_name=instructor_form.instructor_sur_name.data,
                        first_name=instructor_form.instructor_first_name.data,
                        specialization=instructor_form.specialization.data,
                        facebook=instructor_form.facebook.data,
                        linkedin=instructor_form.linkedin.data,
                        twitter=instructor_form.twitter.data,
                        image=filename
                    )
                    educator.password = form.password.data
                    db.session.add(educator)

                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('main_bp.login'))

            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred during registration: {str(e)}", 'danger')
                return render_template('register.html', form=form, student_form=student_form, instructor_form=instructor_form)

        else:
            flash("Please correct the errors in the form.", "danger")

    return render_template('register.html', form=form, student_form=student_form, instructor_form=instructor_form)

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.password = form.new_password.data
            db.session.commit()
            flash('Your password has been updated.', 'success')
            if(current_user.role == 'educator'):
                return redirect(url_for('main_bp.instructor_profile'))
            else:
                return redirect(url_for('main_bp.student_profile'))
    return render_template('change_password.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.home'))

@main_bp.route('/instructor/profile', methods=['GET', 'POST'])
@login_required
def instructor_profile():
    form = UpdateInstructorProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        # Optional educator fields
        if hasattr(current_user, 'first_name'):
            current_user.first_name = form.first_name.data
            current_user.sur_name = form.sur_name.data
            current_user.facebook = form.facebook.data
            current_user.linkedin = form.linkedin.data
            current_user.twitter = form.twitter.data

        # Handle image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)
            current_user.image = f'uploads/{filename}'

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main_bp.instructor_profile'))

    return render_template('instructor/profile.html', form=form)



@main_bp.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    form = UpdateStudentProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        # Optional educator fields
        if hasattr(current_user, 'first_name'):
            current_user.first_name = form.first_name.data
            current_user.sur_name = form.sur_name.data
            current_user.facebook = form.facebook.data
            current_user.linkedin = form.linkedin.data
            current_user.twitter = form.twitter.data

        # Handle image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)
            current_user.image = f'uploads/{filename}'

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main_bp.student_profile'))

    return render_template('student/profile.html', form=form)


@main_bp.route('/settings')
def settings():
    return render_template('settings.html')

@main_bp.route('/educators')
def educators():
    # Fetch all users with the role of 'instructor'
    educators = Educator.query.all()
    return render_template('educators.html', educators=educators)

@main_bp.route('/students')
def students():
    # Fetch all users with the role of 'student'
    students = Student.query.all()
    return render_template('students.html', students=students)

@main_bp.route('/courses')
def courses():
    # Fetch all users with the role of 'courses'
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@main_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)

    # Check if current user is a student and already enrolled
    is_student = current_user.is_authenticated and current_user.role == 'student'

    already_enrolled = False
    if is_student:
        # Check for existing enrollment
        already_enrolled = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=course.id
        ).first() is not None

    return render_template('course_details.html', course=course, is_student=is_student, already_enrolled=already_enrolled)


@main_bp.route('/enroll/<int:course_id>')
@login_required
@role_required('student')
def enroll_in_course(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user.role != 'student':
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('main_bp.course_detail', course_id=course_id))

    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('main_bp.course_detail', course_id=course_id))

    new_enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course.id,
        enrollment_date=datetime.utcnow()
    )
    db.session.add(new_enrollment)
    db.session.commit()

    flash('You have successfully enrolled in the course!', 'success')
    return redirect(url_for('main_bp.course_detail', course_id=course_id))

@main_bp.route('/my-courses')
@role_required('student')
def my_courses():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student/courses.html', enrollments=enrollments)



# Admin Routes
@main_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    users = User.query.all()
    courses = Course.query.all()
    return render_template('admin/dashboard.html', users=users, courses=courses)

# Instructor Routes
@main_bp.route('/instructor/courses')
@login_required
@role_required('educator')
def instructor_courses():
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    form = DiscussionRoomForm()
    material_form = LearningMaterialForm()
    return render_template('instructor/courses.html', courses=courses, material_form=material_form, form=form)

@main_bp.route('/course/create', methods=['GET', 'POST'])
@login_required
@role_required('educator')
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        file = request.files.get('image')
        if file and allowed_file(file.filename):
            filename = f"{form.code.data}_{form.title.data}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
            except Exception as e:
                flash(f"Failed to save the file: {e}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload a valid image.", "danger")
            return redirect(request.url)
        course = Course(
            code=form.code.data,
            title=form.title.data,
            unit=form.unit.data,
            semester=form.semester.data,
            level=form.level.data,
            description=form.description.data,
            instructor_id=current_user.id,
            image=filename if form.image.data else None,
            session=form.session.data
        )
        db.session.add(course)
        db.session.commit()
        print("saved")
        flash('Course created successfully!', 'success')
        return redirect(url_for('main_bp.instructor_courses'))
    return render_template('instructor/create_course.html', form=form)

@main_bp.route('/course/<int:course_id>/add_material', methods=['GET', 'POST'])
@login_required
@role_required('educator')
def add_learning_material(course_id):
    course = Course.query.get_or_404(course_id)

    # Ensure current_user is the instructor of the course
    if course.instructor_id != current_user.id:
        flash('You do not have permission to add materials to this course.', 'danger')
        return redirect(url_for('main_bp.instructor_courses'))

    form = LearningMaterialForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['LEARNING_MATERIALS_FOLDER'], filename)

        try:
            file.save(file_path)
            material = LearningMaterial(
                title=form.title.data,
                description=form.description.data,
                file_path=filename,
                course_id=course.id
            )
            db.session.add(material)
            db.session.commit()
            flash('Learning material added successfully!', 'success')
            return redirect(url_for('main_bp.instructor_courses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving material: {e}', 'danger')

    return render_template('instructor/courses.html', form=form, course=course)

@main_bp.route('/material/delete/<int:material_id>', methods=['POST'])
@login_required
@role_required('educator')
def delete_material(material_id):
    material = LearningMaterial.query.get_or_404(material_id)
    
    # Optional: ensure current user owns the course
    if material.course.instructor_id != current_user.id:
        flash("You are not authorized to delete this material.", "danger")
        return redirect(url_for('main_bp.instructor_courses'))

    try:
        # Delete file from filesystem
        file_path = os.path.join(app.config['LEARNING_MATERIALS_FOLDER'], material.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(material)
        db.session.commit()
        flash("Material deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting material: {e}", "danger")

    return redirect(url_for('main_bp.instructor_courses'))

@main_bp.route('/course/<int:course_id>/add-forum', methods=['POST'])
@login_required
def add_discussion_room(course_id):
    if current_user.role != 'educator':
        abort(403)
    title = request.form.get('title')
    description = request.form.get('description')

    if not title or not description:
        flash('All fields are required.', 'danger')
        return redirect(request.referrer)

    new_room = DiscussionRoom(title=title, description=description, course_id=course_id)
    db.session.add(new_room)
    db.session.commit()
    flash('Discussion room created successfully.', 'success')
    return redirect(request.referrer)

@main_bp.route('/discussion-room/<int:room_id>')
def view_discussion_room(room_id):
    room = DiscussionRoom.query.get_or_404(room_id)
    messages = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp).all()
    return render_template('instructor/chat.html', room=room, messages=messages)

@main_bp.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('instructor/course.html', course=course)

# Student Routes


# @main_bp.route('/student/courses')
# @login_required
# @role_required('student')
# def student_courses():
#     enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
#     return render_template('student/courses.html', enrollments=enrollments)







from flask_socketio import SocketIO, join_room, leave_room, emit

# @app.route('/room/<room_id>')
# def room(room_id):
#     # Simulate room title loading
#     room_info = {'id': room_id, 'title': f"Room {room_id}"}
#     return render_template('index.html', room=room_info)

@socketio.on('join')
def handle_join(data):
    join_room(data['room'])
    emit('status', {'msg': f"{data['username']} has joined the room."}, room=data['room'])

@socketio.on('post_question')
def handle_question(data):
    emit('new_question', {
        'question': data['question'],
        'username': data['username'],
        'role': data['role']
    }, room=data['room'])

@socketio.on('send_reply')
def handle_reply(data):
    # Save to DB
    message = Message(
        room_id=int(data['room']),
        user_id=current_user.id,
        username=current_user.username,
        content=data['reply'],
        role=current_user.role,
        reply_id=data['reply_id'],
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()

    # Emit to room
    emit('new_reply', message.to_dict(), room=data['room'])

@socketio.on('mark_reply')
def mark_reply(data):
    msg = Message.query.filter_by(reply_id=data['reply_id']).first()
    if msg:
        msg.status = data['status']
        db.session.commit()

    emit('mark_update', {
        'reply_id': data['reply_id'],
        'status': data['status']
    }, to=data['room'])
    
@socketio.on('leave')
def on_leave(data):
    room_id = data['room_id']
    leave_room(room_id)
        




















# Quiz Routes
@main_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        if user_answer == quiz.answer:
            # Award points
            gamification = Gamification.query.filter_by(user_id=current_user.id).first()
            gamification.points += 50
            db.session.commit()
            flash('Correct answer! +50 points', 'success')
        else:
            flash('Incorrect answer. Try again!', 'danger')
        return redirect(url_for('main_bp.view_course', course_id=quiz.course_id))
    
    return render_template('quiz.html', quiz=quiz)

# Gamification Routes
@main_bp.route('/leaderboard')
def leaderboard():
    top_users = Gamification.query.order_by(
        Gamification.points.desc()
    ).limit(10).all()
    return render_template('leaderboard.html', users=top_users)

# Collaboration Routes
@main_bp.route('/course/<int:course_id>/chat')
@login_required
def course_chat(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('chat.html', course=course)

# Error Handlers
@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main_bp.route('/course/<int:course_id>/quiz/create', methods=['GET', 'POST'])
@login_required
@role_required('instructor')
def create_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            question=form.question.data,
            options=form.options.data.split(','),
            answer=form.answer.data,
            course_id=course.id
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('main_bp.instructor_courses'))
    return render_template('instructor/create_quiz.html', form=form, course=course)




# @main_bp.route('/chat')
# def chat():
#     return render_template('chat.html')

# @main_bp.route('/earn_points/<task_id>')
# def earn_points(task_id):
#     points = 10  # Points for completing the task
#     current_user.points += points
#     db.session.commit()
#     return redirect(url_for('dashboard'))

# def award_points(user_id, points):
#     user_g = Gamification.query.filter_by(user_id=user_id).first()
#     user_g.points += points
#     if user_g.points >= 1000:
#         user_g.badges.append("quiz_master")
#     db.session.commit()



# @main_bp.route('/quiz/<int:quiz_id>', methods=['POST'])
# def submit_quiz(quiz_id):
#     quiz = Quiz.query.get(quiz_id)
#     user_answer = request.form.get('answer')
#     if user_answer == quiz.answer:
#         award_points(current_user.id, 50)
#         return "Correct!"
#     return "Incorrect!"