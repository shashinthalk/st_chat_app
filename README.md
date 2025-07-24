# Simple Flask Q&A API

A lightweight Flask API that provides Q&A functionality using external knowledge base API with intelligent fallback system.

## Features

- **Health Check**: `/health` - Check API status and knowledge base connectivity
- **Query**: `/query` - Submit questions and get comprehensive answers
- **External API Integration**: Uses `https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data`
- **Smart Fallback System**: Falls back to cached/mock data if external API is unavailable
- **Advanced Matching**: Keyword recognition and context-aware responses
- **Cache Management**: Built-in caching with `/cache/info` and `/cache/clear` endpoints
- **API Testing**: `/test-api` endpoint for debugging external API connectivity
- **Docker deployment ready**
- **Production-ready with Gunicorn**
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
  "available_endpoints": ["/health", "/query", "/cache/info", "/cache/clear", "/test-api"],
  "knowledge_base": {
    "status": "connected|fallback_mode|disconnected",
    "data_count": 4,
    "cache_info": {
      "cached": true,
      "cache_status": "success|fallback|mock",
      "cached_entries": 4
    }
  }
}
```

### Query Endpoint
```bash
POST /query
Content-Type: application/json

{
  "question": "can u develop kotlin api backend"
}
```

**Success Response (200):**
```json
{
  "matched": true,
  "question": "can u develop kotlin api backend",
  "answer": {
    "title": "Kotlin API Backend Development",
    "subtitle": "Expertise in Building Scalable and Secure APIs",
    "about": "Detailed explanation...",
    "projects": [
      {
        "title": "Kotlin API Backend",
        "description": "A scalable and secure API backend built using Kotlin and Spring Boot",
        "technologies": ["Kotlin", "Spring Boot"],
        "link": "#"
      }
    ],
    "whyWorkWithMe": ["Reason 1", "Reason 2", "..."],
    "callToAction": {
      "heading": "Ready to Get Started?",
      "message": "Contact message...",
      "buttonText": "Contact Me",
      "buttonLink": "/contact"
    }
  },
  "metadata": {
    "id": "6880bed079737a9e77620472",
    "match_type": "knowledge_base",
    "data_source": "success|fallback|mock"
  }
}
```

**Available Questions:**
- "can u develop kotlin api backend"
- "tell me about yourself" / "tell me about your self"
- "education and career experience"
- "can u design a photo"

**Smart Keyword Matching:**
- **Kotlin development** → matches development/API questions
- **About/self** → matches personal background questions
- **Education/career** → matches professional background
- **Design** → matches design-related questions

**No Match Response (404):**
```json
{
  "error": "No matching answer found for your question",
  "question": "Your question here",
  "matched": false,
  "available_questions": ["can u develop kotlin api backend", "..."],
  "suggestions": [
    "Try asking about Kotlin development, career experience, or personal background",
    "Ask 'can u develop kotlin api backend' or 'tell me about yourself'",
    "Check the available questions list above for inspiration"
  ],
  "total_available": 4,
  "data_source": "fallback"
}
```

### Cache Management
```bash
# Get cache information
GET /cache/info

# Clear cache (force fresh API call)
POST /cache/clear
```

### API Testing
```bash
# Test external API connectivity
GET /test-api
```

## External API Integration

### Primary Data Source
- **URL**: `https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data`
- **Authentication**: JWT Bearer token
- **Caching**: 5-minute cache to reduce API calls
- **Fallback**: Automatic fallback to mock data if API fails

### Data Structure
The external API returns structured knowledge base entries:
```json
[
  {
    "_id": "unique_id",
    "question": "user question",
    "answers": {
      "title": "Response title",
      "subtitle": "Response subtitle", 
      "about": "Detailed explanation",
      "projects": [...],
      "whyWorkWithMe": [...],
      "callToAction": {...}
    }
  }
]
```

### Fallback System
- **Primary**: External API call
- **Secondary**: 5-minute cached data
- **Tertiary**: Mock data (built-in knowledge base)
- **Status Indicators**: `success` | `fallback` | `mock`

## Adding More Q&A Data

### Option 1: Update External API
The primary data source is the external n8n webhook. Update your knowledge base there.

### Option 2: Update Mock Data (Fallback)
Edit `app/services/knowledge_base.py` and update the `mock_data` array:

```python
self.mock_data = [
    {
        "_id": "new_id",
        "question": "Your new question?",
        "answers": {
            "title": "Response Title",
            "subtitle": "Response Subtitle",
            "about": "Your detailed answer here",
            "projects": [],
            "whyWorkWithMe": [],
            "callToAction": {
                "heading": "Ready to Get Started?",
                "message": "Contact message",
                "buttonText": "Contact Me", 
                "buttonLink": "/contact"
            }
        }
    }
]
```

## Testing

### Comprehensive Testing
```bash
# Test external API integration
./test-external-api.sh

# Local build and test
./build-and-test.sh
```

### Manual Testing
```bash
# Health check
curl http://localhost:5001/health

# Kotlin development query
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "can u develop kotlin api backend"}' \
  http://localhost:5001/query

# About query
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "tell me about yourself"}' \
  http://localhost:5001/query

# API connection test
curl http://localhost:5001/test-api

# Cache management
curl http://localhost:5001/cache/info
curl -X POST http://localhost:5001/cache/clear
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
SERVER_IP=your.server.ip.address
USERNAME=your_ssh_username
SSH_PRIVATE_KEY=your_ssh_private_key_content
```

## Project Structure

```
st_chat_app/
├── .github/workflows/deploy-flask.yml    # GitHub Actions CI/CD
├── app/
│   ├── __init__.py                       # Flask app factory
│   ├── data.py                          # Legacy fallback data
│   ├── services/
│   │   ├── __init__.py
│   │   └── knowledge_base.py            # External API integration
│   └── api/
│       ├── __init__.py
│       └── routes.py                    # API endpoints
├── nginx-api.shashinthalk.cc.conf       # Nginx reverse proxy config
├── nginx-setup.sh                       # Automated Nginx setup
├── test-api.sh                         # Production API testing
├── test-external-api.sh                # External API integration testing
├── deploy-simple.sh                    # Manual deployment script
├── build-and-test.sh                   # Build & test script
├── Dockerfile                          # Docker configuration
├── requirements.txt                    # Python dependencies (includes requests)
├── DEPLOYMENT.md                       # Complete deployment guide
└── README.md                          # This file
```

## Deployment

The application is ready for deployment with:
- External API integration with smart fallback system
- Docker containerization
- Gunicorn WSGI server  
- Health checks and API testing endpoints
- Production-ready configuration
- **Automated CI/CD pipeline**
- Comprehensive testing suite
- Nginx reverse proxy support

Perfect for connecting to AI models later - the structured response format is ideal for ML analysis! 🤖 