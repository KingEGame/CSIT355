from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from .routes.auth_routes import auth_bp
from .routes.student_routes import students
from .routes.professor_routes import professors_bp
from .routes.course_routes import courses_bp
from .routes.admin_routes import admin
import os

def create_app(config=None):
    app = Flask(__name__)
    
    # Basic configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///course_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload folder configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Secret key for session management and flash messaging
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students)
    app.register_blueprint(professors_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin)
    
    return app 