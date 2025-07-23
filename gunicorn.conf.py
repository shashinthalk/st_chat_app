"""
Gunicorn Configuration for Flask Sentence Transformer API

This configuration file provides production-ready settings for running
the Flask application with Gunicorn WSGI server.
"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes - optimized for lightweight ML model
workers = 1  # Single worker for memory efficiency with ML models
worker_class = "sync"
worker_connections = 1000
timeout = 600  # Extended timeout for first request processing with model files
keepalive = 2

# Restart workers after fewer requests due to memory usage
max_requests = 100
max_requests_jitter = 50

# Memory management
worker_tmp_dir = "/dev/shm"  # Use shared memory for temporary files

# Preload application for better performance
preload_app = True

# User and group to run as (if running as root)
# user = "nobody"
# group = "nogroup"

# Logging
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'flask-sentence-transformer-api'

# Graceful timeout for worker restart
graceful_timeout = 30

# Temporary directory for worker heartbeat
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Environment variables
raw_env = [
    'FLASK_ENV=production',
]

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Sentence Transformer API server is ready. Listening on: %s", bind)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid) 