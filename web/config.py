import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 1800))  # 30 minutes
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USER', 'db')}:"
        f"{os.getenv('DB_PASSWORD', 'db')}@"
        f"{os.getenv('DB_HOST', '127.0.0.1')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 'csit_555')}"
        f"?charset={os.getenv('DB_CHARSET', 'utf8mb4')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 1800)),
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'connect_args': {
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', 10))
        }
    }

    # Upload folder
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'web', 
        os.getenv('UPLOAD_FOLDER', 'uploads')
    )
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    # In production, SECRET_KEY must be set in environment
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment")

class TestingConfig(Config):
    TESTING = True
    # Use separate test database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('TEST_DB_USER', 'db')}:"
        f"{os.getenv('TEST_DB_PASSWORD', 'db')}@"
        f"{os.getenv('TEST_DB_HOST', '127.0.0.1')}:"
        f"{os.getenv('TEST_DB_PORT', '3306')}/"
        f"{os.getenv('TEST_DB_NAME', 'csit_555_test')}"
        f"?charset={os.getenv('DB_CHARSET', 'utf8mb4')}"
    )

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
