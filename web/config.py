import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path='D:/MSU/Database/Project/.env')

class Config:
    # Add session configuration
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://db:csit_555@localhost:3306/csit555')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://db:csit_555@localhost:3306/csit555')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 