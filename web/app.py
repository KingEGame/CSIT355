from flask import Flask
from .models import db
from .routes import auth, courses, professors
from .config import config
from flask_session import Session

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    Session(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(courses)
    app.register_blueprint(professors)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True) 