"""
Configuration Management

This module handles application configuration using environment variables
with sensible defaults for development and production environments.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # MongoDB settings
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/?retryWrites=true&w=majority&appName=n8n-automation-data'
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE') or 'automation_with_ai_data'
    MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION') or 'knowledge_base'
    
    # Sentence Transformer settings
    MODEL_NAME = os.environ.get('MODEL_NAME') or 'all-MiniLM-L6-v2'
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', '0.6'))
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', '5001'))
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/flask_app.log')
    
    @staticmethod
    def validate_config():
        """
        Validate that all required configuration values are present.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        required_vars = ['MONGODB_URI', 'MONGODB_DATABASE', 'MONGODB_COLLECTION']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var) and not hasattr(Config, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        # Validate similarity threshold
        threshold = Config.SIMILARITY_THRESHOLD
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"SIMILARITY_THRESHOLD must be between 0.0 and 1.0, got {threshold}")


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        """Initialize production-specific configurations."""
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    MONGODB_DATABASE = 'test_sentence_transformer_db'
    SIMILARITY_THRESHOLD = 0.5  # Lower threshold for testing


# Configuration mapping for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 