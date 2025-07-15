# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate



db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
admin = Admin(name='Elearning Admin', template_mode='bootstrap3')
socketio = SocketIO()


# login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import here to avoid circular dependency
    return User.query.get(int(user_id))

def create_app():
    # Ensure the upload folder exists
    UPLOAD_FOLDER = 'app/static/uploads'
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
    app.config['LEARNING_MATERIALS_FOLDER'] = os.path.join(app.root_path, 'static', 'learning_materials')
    os.makedirs(app.config['LEARNING_MATERIALS_FOLDER'], exist_ok=True)
    app.config['SECRET_KEY'] = 'a7d11f9fcb14e359a348fa8b15ea021c60b90618af85c5dacb98544bc5e21f03'
    app.config.from_object(Config)
    # app.config.from_object('config.Config')  # Load configuration
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    socketio.init_app(app)
    migrate.init_app(app, db)

    # Import models (ensure they're defined before creating views)
    from app.models import User, Course  # Adjust the import path

    # Add admin views
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Course, db.session))

    # Register blueprints (routes)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # @socketio.on('join')
    # def on_join(data):
    #     room_id = data['room_id']
    #     join_room(room_id)

    # @socketio.on('leave')
    # def on_leave(data):
    #     room_id = data['room_id']
    #     leave_room(room_id)

    # @socketio.on('message')
    # def handle_message(data):
    #     emit('message', data, room=data['room_id'])
    
    # @socketio.on('connect')
    # def handle_connect():
    #     emit('status', {'msg': 'Connected to the chat'})

    # @socketio.on('send_message')
    # def handle_message(data):
    #     new_message = Message(content=data['message'], user_id=data['user_id'])
    #     db.session.add(new_message)
    #     db.session.commit()
    #     emit('receive_message', {'message': new_message.content, 'user': new_message.author.username}, broadcast=True)

    return app