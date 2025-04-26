from web.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

with app.app_context():
    # Try to execute a simple query
    result = db.session.execute(text('SELECT * FROM student')).scalar()
    print(f"Database connection successful! Test query result: {result}") 