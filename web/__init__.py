from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from .routes.auth_routes import auth_bp
from .routes.student_routes import students
from .routes.professor_routes import professors_bp
from .routes.course_routes import courses_bp
from .routes.admin_routes import admin
import os
from dotenv import load_dotenv
from .config import Config

# Load environment variables from .env
load_dotenv()

def create_app(config=None):
    app = Flask(__name__)
    
    # Load the configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(students)
    app.register_blueprint(professors_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(admin)
    
    return app 