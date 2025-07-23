"""
Production Gunicorn Configuration for 3 vCPU, 8GB RAM Server
Optimized for sentence-transformer ML workload with memory management
"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# CRITICAL: Optimized worker configuration for 8GB RAM server
# Formula: (Total RAM - System Overhead) / Expected Memory per Worker
# 8GB - 2GB system = 6GB available
# Each worker with model: ~1.5GB peak, so 3 workers max safely
workers = 3  # Perfect for 3 vCPU server
worker_class = "sync"
worker_connections = 100  # Reduced for ML workload

# Timeouts optimized for model loading
timeout = 120  # Reasonable timeout for production
keepalive = 2
graceful_timeout = 60

# CRITICAL: Worker lifecycle management to prevent memory leaks
max_requests = 50  # Low number to restart workers frequently
max_requests_jitter = 10  # Prevent thundering herd

# Memory optimization
worker_tmp_dir = "/dev/shm"  # Use shared memory
preload_app = True  # Load model once, fork to workers

# Process limits and resource management
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging optimized for production monitoring
loglevel = 'info'
accesslog = "/app/logs/access.log"
errorlog = "/app/logs/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s %(p)s'

# Process naming for monitoring
proc_name = 'flask-sentence-api'

# Environment variables for production
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=1',
    'PYTHONDONTWRITEBYTECODE=1',
]

# Hooks for monitoring and debugging
def when_ready(server):
    """Called when server is ready."""
    server.log.info("Production server ready. Workers: %d, Timeout: %ds", workers, timeout)

def worker_int(worker):
    """Called when worker receives INT/QUIT."""
    worker.log.info("Worker %s gracefully shutting down", worker.pid)

def post_worker_init(worker):
    """Called after worker initialization."""
    worker.log.info("Worker %s initialized with model loaded", worker.pid)
    
    # Import and log model info for debugging
    try:
        from app.models.sentence_model_minimal import get_sentence_model_minimal
        model = get_sentence_model_minimal()
        worker.log.info("Worker %s: Model loaded successfully", worker.pid)
    except Exception as e:
        worker.log.error("Worker %s: Model loading failed: %s", worker.pid, e)

def worker_abort(worker):
    """Called when worker aborted."""
    worker.log.error("Worker %s aborted (likely OOM or timeout)", worker.pid)

def pre_fork(server, worker):
    """Called before worker fork."""
    server.log.info("Forking worker %s", worker.pid)

def post_fork(server, worker):
    """Called after worker fork."""
    # Force garbage collection after fork
    import gc
    gc.collect()
    server.log.info("Worker %s forked successfully", worker.pid) 