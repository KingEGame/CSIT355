from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from .routes.auth_routes import auth
from .routes.student_routes import students
from .routes.professor_routes import professors
from .routes.course_routes import courses
from .routes.admin_routes import admin
import os
from dotenv import load_dotenv
from .config import Config
from flask_migrate import Migrate

# Load environment variables from .env
load_dotenv()

def create_app(config=None):
    app = Flask(__name__)
    
    # Load the configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(students)
    app.register_blueprint(professors)
    app.register_blueprint(courses)
    app.register_blueprint(admin)
    
    return app