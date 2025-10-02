import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Data processing configuration
    MAX_ROWS = 100000  # Maximum rows to process
    MAX_COLUMNS = 1000  # Maximum columns to process
    
    # Dataset storage settings
    DATASET_EXPIRY = timedelta(hours=24)  # Datasets expire after 24 hours
    CLEANUP_INTERVAL = timedelta(hours=1)  # Run cleanup every hour
    
    # API request throttling
    THROTTLE_INTERVAL = 1.0  # Minimum seconds between requests
    
    # Log settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CORS configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'INFO'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    SECRET_KEY = os.environ.get('SECRET_KEY')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
