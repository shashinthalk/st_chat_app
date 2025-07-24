FROM python:3.10-slim

# Create user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser run.py .
COPY --chown=appuser:appuser gunicorn.conf.py .

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expose port
EXPOSE 5001

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "run:app"] 