# Flask Q&A API with AI-Powered Matching

A Flask API that provides intelligent question-and-answer functionality using AI transformer models for semantic matching.

## 🚀 Features

- **🤖 AI-Powered Matching**: Uses external transformer model for intelligent question matching
- **🌐 External Knowledge Base**: Integrates with n8n webhook for dynamic knowledge base data
- **🔄 Smart Fallback System**: Automatically falls back to mock data if external services are unavailable
- **🚢 Docker Ready**: Fully containerized for easy deployment
- **🔄 CI/CD Pipeline**: Automated deployment via GitHub Actions

## 🏗️ Architecture

```
User Question → Flask API → Extract Dataset → AI Transformer Model → Parse Response → Return Answer Content
                    ↓
               External Knowledge Base API (with JWT auth)
                    ↓
               Fallback to Mock Data (if API fails)
```

### AI Integration

- **Transformer Model**: `http://95.111.228.138:5002/query`
- **Request Format**: `{"question": "user question", "dataset": ["q1", "q2", ...]}`
- **Confidence Threshold**: 0.5 (configurable)

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | System health with AI model and knowledge base status |
| `/query` | POST | AI-powered question matching and response |
| `/cache/info` | GET | Cache status and dataset information |
| `/cache/clear` | POST | Clear knowledge base cache |
| `/test-api` | GET | Test external knowledge base API connection |
| `/test-transformer` | GET/POST | Test AI transformer model connection |

## 🔧 Usage Examples

### Query with AI Matching

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "what can you do with kotlin"}' \
  http://localhost:5001/query
```

**Response** (200 OK):
```json
{
  "title": "Kotlin API Backend Development",
  "subtitle": "Expertise in Building Scalable and Secure APIs",
  "about": "As a Full Stack Engineer with experience in Kotlin...",
  "projects": [...],
  "whyWorkWithMe": [...],
  "callToAction": {...}
}
```

### Health Check

```bash
curl http://localhost:5001/health
```

## 🚀 Quick Start

### Local Development

```bash
# Clone and setup
git clone <repository>
cd st_chat_app

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

### Docker Deployment

```bash
# Build and run
docker build -t flask-qa-api .
docker run -d --name flask-qa-container -p 5001:5001 flask-qa-api
```

## 🔧 Configuration

### AI Model Settings

```python
# In app/services/knowledge_base.py
confidence_threshold = 0.5  # Adjust matching sensitivity
timeout = 15  # API request timeout in seconds
cache_expiry = 300  # Cache duration in seconds (5 minutes)
```

### Environment Variables

```bash
FLASK_ENV=production
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

## 🚢 Production Deployment

### GitHub Actions CI/CD

Automated pipeline includes:

- **Building**: Docker image creation
- **Testing**: Basic Flask app validation
- **Deployment**: Automatic server deployment on push to main

### Required GitHub Secrets

Set these secrets in your GitHub repository:

```bash
SERVER_IP=your.server.ip.address
USERNAME=your_ssh_username
SSH_PRIVATE_KEY=your_ssh_private_key_content
```

### Nginx Reverse Proxy

The API includes production-ready Nginx configuration with SSL, rate limiting, and security headers.

```bash
# Setup Nginx (run on server)
./nginx-setup.sh
```

## 🤝 Integration Guide

### Adding New Questions

Questions are automatically extracted from the external knowledge base API. To add new questions:

1. Update your n8n knowledge base webhook
2. Clear the cache: `POST /cache/clear`
3. New questions will be included in the AI model dataset

### Adjusting AI Sensitivity

```python
# In app/services/knowledge_base.py, line ~185
confidence_threshold = 0.3  # More sensitive (more matches)
confidence_threshold = 0.7  # Less sensitive (stricter matching)
```

## 🛠️ Development

### Project Structure

```
st_chat_app/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── api/routes.py         # API endpoints
│   ├── services/knowledge_base.py  # AI & external API integration
│   └── data.py               # Fallback data
├── gunicorn.conf.py          # Production server config
├── Dockerfile                # Container configuration
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## 🎯 Use Cases

- **Customer Support**: Intelligent FAQ matching and responses
- **Knowledge Management**: Semantic search through documentation
- **Personal Assistant**: Context-aware question answering
- **Content Discovery**: Find relevant content based on natural language queries

---

Built with ❤️ using Flask, AI Transformers, and modern DevOps practices. 