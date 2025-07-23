"""
Simple Flask Application Factory
"""

from flask import Flask


def create_app():
    """
    Create and configure Flask app instance.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Register API routes
    from app.api.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app 