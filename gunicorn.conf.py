"""
Simple Gunicorn Configuration for Flask Q&A API
"""

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker configuration
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Worker lifecycle management
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = 'info'
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = 'flask-qa-api' 