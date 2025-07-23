"""
Flask Application Factory

This module implements the application factory pattern for creating Flask app instances
with proper configuration, database initialization, and blueprint registration.
"""

import logging
import os
from flask import Flask, jsonify
from app.config import Config
from app.database.mongodb import init_db


def create_app(config_class=Config):
    """
    Application factory function that creates and configures Flask app instance.
    
    Args:
        config_class: Configuration class to use for the app
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    configure_logging(app)
    
    # Initialize database connection
    init_db(app)
    
    # Initialize sentence transformer model with fallback support
    try:
        # Try optimized model first
        from app.models.sentence_model_optimized import init_sentence_model_optimized
        init_sentence_model_optimized(app)
        app.logger.info("Flask application created successfully with optimized model")
    except ImportError as e:
        if 'psutil' in str(e):
            # Fallback to minimal model if psutil is not available
            app.logger.warning("psutil not available, falling back to minimal model")
            from app.models.sentence_model_minimal import init_sentence_model_minimal
            init_sentence_model_minimal(app)
            app.logger.info("Flask application created successfully with minimal model (psutil fallback)")
        else:
            raise
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def configure_logging(app):
    """Configure application logging based on environment."""
    if not app.debug and not app.testing:
        # Production logging configuration
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = logging.FileHandler('logs/flask_app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
    else:
        # Development logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def register_error_handlers(app):
    """Register global error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        app.logger.warning(f"Bad request: {error}")
        return jsonify({
            'error': 'Bad request. Please check your request format.',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': 'Endpoint not found',
            'available_endpoints': ['/health', '/query'],
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'error': 'Method not allowed for this endpoint',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors."""
        app.logger.error(f"Unexpected error: {error}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'status_code': 500
        }), 500 