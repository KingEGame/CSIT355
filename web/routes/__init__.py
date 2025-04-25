from .auth_routes import auth_bp
from .course_routes import courses_bp
from .professor_routes import professors_bp
from .student_routes import students
from .admin_routes import admin

__all__ = ['auth_bp', 'courses_bp', 'professors_bp', 'students', 'admin'] 