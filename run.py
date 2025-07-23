#!/usr/bin/env python3
"""
Flask Application Entry Point

This module serves as the main entry point for the Flask sentence transformer API.
It uses the application factory pattern and handles configuration and startup.
"""

import os
import sys
from app import create_app
from app.config import config, Config

# Create Flask app instance for Gunicorn
try:
    Config.validate_config()
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config[config_name])
except Exception as e:
    print(f"Failed to create application: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    """Main function to start the Flask development server (local development only)."""
    try:
        # Get host and port from config
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 5001)
        debug = app.config.get('DEBUG', False)
        
        app.logger.info(f"Starting Flask development server on {host}:{port}")
        app.logger.info(f"Configuration: {os.environ.get('FLASK_ENV', 'development')}")
        app.logger.info(f"Debug mode: {debug}")
        app.logger.warning("WARNING: This is a development server. Use Gunicorn for production.")
        
        # Start the Flask development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start application: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 