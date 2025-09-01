"""
Configuration file for EduVerse application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'eduverse')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', '')
    
    # Hugging Face API
    HF_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    
    # IntaSend Payment Configuration
    INTASEND_PUBLISHABLE_KEY = os.getenv('INTASEND_PUBLISHABLE_KEY')
    INTASEND_SECRET_KEY = os.getenv('INTASEND_SECRET_KEY')
    INTASEND_TEST_MODE = os.getenv('INTASEND_TEST_MODE', 'True').lower() == 'true'
    
    # Application Configuration
    SUBSCRIPTION_AMOUNT = float(os.getenv('SUBSCRIPTION_AMOUNT', '12.00'))
    SUBSCRIPTION_CURRENCY = os.getenv('SUBSCRIPTION_CURRENCY', 'USD')
    SUBSCRIPTION_DURATION_DAYS = int(os.getenv('SUBSCRIPTION_DURATION_DAYS', '30'))
    TRIAL_DURATION_DAYS = int(os.getenv('TRIAL_DURATION_DAYS', '7'))
    MAX_FLASHCARDS_PER_GENERATION = int(os.getenv('MAX_FLASHCARDS_PER_GENERATION', '20'))
    MIN_FLASHCARDS_PER_GENERATION = int(os.getenv('MIN_FLASHCARDS_PER_GENERATION', '1'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

