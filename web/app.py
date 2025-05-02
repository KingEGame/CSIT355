from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from web.models import db, Student, Professor
from web.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated

@login_manager.user_loader
def load_user(user_id):
    # Check if the user is a student or professor
    user = Student.query.get(user_id) or Professor.query.get(user_id)
    return user

# Add teardown context
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Register blueprints
from web.routes.auth_routes import auth
from web.routes.professor_routes import professors
from web.routes.student_routes import students
from web.routes.admin_routes import admin

# Register the auth blueprint without a prefix to handle the root route ('/')
app.register_blueprint(auth)
app.register_blueprint(professors, url_prefix='/professors')
app.register_blueprint(students, url_prefix='/students')
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)