from flask import Flask
from flask_migrate import Migrate, upgrade
from web.models import db
from web.config import config
from web import create_app

app = create_app()

if __name__ == '__main__':
    app.run()