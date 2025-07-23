# Simple Flask Q&A API

A lightweight Flask API that provides Q&A functionality using hardcoded JSON data.

## Features

- **Health Check**: `/health` - Check API status
- **Query**: `/query` - Submit questions and get answers
- Simple JSON-based Q&A matching
- Docker deployment ready
- Production-ready with Gunicorn

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Docker Deployment

```bash
# Build the image
docker build -t flask-qa-api .

# Run the container
docker run -d --name flask-qa-api -p 5001:5001 flask-qa-api
```

## API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Flask Q&A API is running",
  "available_endpoints": ["/health", "/query"],
  "data_count": 2
}
```

### Query
```bash
POST /query
Content-Type: application/json

{
  "question": "What is machine learning?"
}
```

**Success Response (200):**
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence...",
  "matched": true
}
```

**No Match Response (404):**
```json
{
  "error": "No matching answer found for your question",
  "question": "Your question here",
  "matched": false,
  "available_questions": ["What is machine learning?", "What is artificial intelligence?"]
}
```

## Adding More Q&A Data

Edit the `app/data.py` file to add more questions and answers:

```python
QA_DATA = [
    {
        "question": "Your question here",
        "answer": "Your answer here"
    },
    # Add more Q&A pairs...
]
```

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── data.py              # Q&A data
│   └── api/
│       └── routes.py        # API endpoints
├── Dockerfile               # Docker configuration
├── gunicorn.conf.py         # Gunicorn configuration
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md               # This file
```

## Testing

```bash
# Health check
curl http://localhost:5001/health

# Query example
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}' \
  http://localhost:5001/query
```

## Deployment

The application is ready for deployment with:
- Docker containerization
- Gunicorn WSGI server
- Health checks
- Production-ready configuration

Perfect for connecting to external ML models or expanding functionality later! 