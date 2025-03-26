from flask import Blueprint

# Define the blueprints first
auth = Blueprint('auth', __name__)
courses = Blueprint('courses', __name__)
professors = Blueprint('professors', __name__)

# Now import the route files
from . import auth_routes, course_routes, professor_routes 