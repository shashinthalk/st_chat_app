# Simple Flask Q&A API

A lightweight Flask API that provides Q&A functionality using hardcoded JSON data.

## Features

- **Health Check**: `/health` - Check API status
- **Query**: `/query` - Submit questions and get answers
- Simple JSON-based Q&A matching with smart keyword recognition
- Docker deployment ready
- Production-ready with Gunicorn
- **GitHub Actions CI/CD** - Automated testing and deployment

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

### Automated Deployment

```bash
# Use the included deployment script
chmod +x deploy-simple.sh
./deploy-simple.sh
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
  "matched": true,
  "match_type": "direct"
}
```

**Smart Keyword Matching:**
- **"AI"** → matches **"artificial intelligence"**
- **"ML"** → matches **"machine learning"**
- Partial text matching for flexible queries

**No Match Response (404):**
```json
{
  "error": "No matching answer found for your question",
  "question": "Your question here",
  "matched": false,
  "available_questions": ["What is machine learning?", "What is artificial intelligence?"],
  "suggestions": ["Try using keywords like: AI, ML, machine learning"]
}
```

## GitHub Actions CI/CD

### Automatic Deployment

The project includes a complete GitHub Actions workflow (`.github/workflows/deploy-flask.yml`) that:

- ✅ **Tests the Flask app** creation and Q&A data loading
- ✅ **Runs API tests** for all endpoints
- ✅ **Builds Docker image** and tests container functionality
- ✅ **Deploys to server** automatically on push to main branch
- ✅ **Performs health checks** to verify successful deployment

### Required GitHub Secrets

Set these secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

```bash
REMOTE_HOST=your.server.ip.address
REMOTE_USER=your_ssh_username
SSH_PRIVATE_KEY=your_ssh_private_key_content
```

### Deployment Workflow

1. **Push to main branch** or create pull request
2. **Automated testing** runs on GitHub runners
3. **Docker image built** and tested
4. **Deployed to server** via SSH (main branch only)
5. **Health checks** verify successful deployment

### Manual Deployment

You can also deploy manually using:

```bash
# Full automated deployment with testing
./deploy-simple.sh

# Or just build and test
./build-and-test.sh
```

## Adding More Q&A Data

Edit the `app/data.py` file to add more questions and answers:

```python
QA_DATA = [
    {
        "question": "What is machine learning?",
        "answer": "Machine learning is a subset of artificial intelligence..."
    },
    {
        "question": "What is artificial intelligence?", 
        "answer": "Artificial Intelligence (AI) is a branch of computer science..."
    },
    # Add your questions here:
    {
        "question": "Your new question?",
        "answer": "Your answer here"
    }
]
```

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment

## Project Structure

```
├── .github/
│   └── workflows/
│       └── deploy-flask.yml     # GitHub Actions CI/CD
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── data.py                  # Q&A data
│   └── api/
│       └── routes.py            # API endpoints
├── Dockerfile                   # Docker configuration
├── gunicorn.conf.py             # Gunicorn configuration
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── deploy-simple.sh             # Manual deployment script
├── build-and-test.sh            # Build and test script
└── README.md                    # This file
```

## Testing

```bash
# Health check
curl http://localhost:5001/health

# Query example
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}' \
  http://localhost:5001/query

# Run comprehensive tests
./build-and-test.sh
```

## Deployment

The application is ready for deployment with:
- Docker containerization
- Gunicorn WSGI server  
- Health checks
- Production-ready configuration
- **Automated CI/CD pipeline**
- Comprehensive testing suite

Perfect for connecting to external ML models or expanding functionality later! 