from .auth_routes import auth_bp as auth
from .course_routes import courses_bp as courses
from .professor_routes import professors_bp as professors
from .student_routes import students
from .admin_routes import admin

__all__ = ['auth', 'courses', 'professors', 'students', 'admin'] 