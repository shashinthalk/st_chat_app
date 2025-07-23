# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY run.py .
COPY gunicorn.conf.py .
COPY .env.example .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port 5001
EXPOSE 5001

# Health check - longer intervals for ML workloads
HEALTHCHECK --interval=60s --timeout=45s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run the application with Gunicorn optimized for ML workloads
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"] 