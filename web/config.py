import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Add session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')  # Add secret key

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://db:db@127.0.0.1:3306/csit_555?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_timeout': 5,
        'connect_args': {
            'connect_timeout': 5
        }
    }
    DEBUG = True

    # Upload folder configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # In production, this must be set in environment

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://db:db@localhost:3306/csit_555'

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
} 