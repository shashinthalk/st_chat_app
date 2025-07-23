# Flask Sentence Transformer API - Refactored Architecture

A production-ready Flask API service with modular architecture that provides semantic search capabilities using sentence-transformers and MongoDB. The application uses proper separation of concerns, dependency injection, and configuration management.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for database, models, API routes, and utilities
- **MongoDB Integration**: Dynamic Q&A data from MongoDB collections with document validation
- **Semantic Search**: Uses `all-MiniLM-L6-v2` sentence transformer model with configurable similarity thresholds
- **Flask Application Factory**: Proper application factory pattern for better testing and configuration management
- **Environment Configuration**: Comprehensive configuration management with environment variables
- **Batch Processing**: Support for batch query processing with top-K results
- **Production Ready**: Docker containerization, health checks, and comprehensive error handling
- **Auto Deployment**: GitHub Actions CI/CD pipeline

## 📋 Prerequisites

- Python 3.10+
- MongoDB (local or cloud instance like MongoDB Atlas)
- Docker (for containerized deployment)
- Git

## 🏗️ Architecture

```
app/
├── __init__.py              # Application factory
├── config.py                # Configuration management
├── api/
│   ├── __init__.py
│   └── routes.py            # API endpoints
├── database/
│   ├── __init__.py
│   └── mongodb.py           # MongoDB operations
├── models/
│   ├── __init__.py
│   └── sentence_model.py    # Sentence transformer service
└── utils/
    ├── __init__.py  
    └── similarity.py        # Similarity calculations
run.py                       # Application entry point
```

## 🛠️ Local Development

### 1. Clone and Setup

```bash
git clone <your-repository>
cd st_chat_app
```

### 2. Environment Configuration

Create a `.env` file based on the example:

```bash
# Copy the example file
cp .env.example .env

# Edit the configuration
nano .env
```

**Required Environment Variables:**

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/sentence_transformer_db
MONGODB_DATABASE=sentence_transformer_db
MONGODB_COLLECTION=qa_documents

# Application Settings
FLASK_ENV=development
FLASK_PORT=5001
SIMILARITY_THRESHOLD=0.6

# Security
SECRET_KEY=your-secure-secret-key-here
```

### 3. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB locally and start the service
# Then create your database and collection
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# Create a cluster on MongoDB Atlas
# Use the connection string format:
# mongodb+srv://username:password@cluster.mongodb.net/sentence_transformer_db
```

### 4. Sample Data

Insert sample documents into MongoDB with this structure:

```json
{
  "question": "What is machine learning?",
  "answers": {
    "title": "Machine Learning Expert",
    "subtitle": "AI & Data Science Specialist",
    "about": "I specialize in machine learning and artificial intelligence...",
    "projects": [
      {
        "name": "ML Model Pipeline",
        "description": "Built end-to-end ML pipeline..."
      }
    ],
    "whyWorkWithMe": [
      "10+ years in ML/AI development",
      "Published research in top conferences"
    ],
    "callToAction": {
      "message": "Ready to build AI solutions?",
      "contact": "Let's discuss your ML project"
    }
  }
}
```

### 5. Install Dependencies and Run

```bash
# Install Python dependencies
pip install -r requirements.txt

# For local development (Flask development server)
python run.py

# For production-like testing (Gunicorn)
gunicorn --config gunicorn.conf.py run:app
```

The API will be available at `http://localhost:5001`

**Note:** The Flask development server warning is normal for local development. Production deployments use Gunicorn automatically.

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t sentence-transformer-flask:latest .

# Run with environment variables (uses Gunicorn in production)
docker run -d \
  --name st-flask-container \
  --restart unless-stopped \
  -p 5001:5001 \
  -e MONGODB_URI="your-mongodb-connection-string" \
  -e SIMILARITY_THRESHOLD="0.6" \
  sentence-transformer-flask:latest
```

**Docker automatically uses Gunicorn WSGI server for production deployment.**

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model": {
    "status": "healthy", 
    "model_name": "all-MiniLM-L6-v2",
    "loaded": true,
    "embedding_dimension": 384
  },
  "database": {
    "status": "healthy",
    "connected": true,
    "document_count": 5
  },
  "config": {
    "similarity_threshold": 0.6,
    "mongodb_database": "sentence_transformer_db",
    "mongodb_collection": "qa_documents"
  }
}
```

### Single Query
```http
POST /query
Content-Type: application/json
```

**Request:**
```json
{
  "question": "How do neural networks work?",
  "threshold": 0.7  // optional, overrides config
}
```

**Success Response (200):**
```json
{
  "matched_question": "How does neural network work?",
  "answers": {
    "title": "Neural Network Specialist",
    "subtitle": "Deep Learning Expert",
    "about": "Neural networks process data through interconnected layers...",
    "projects": [...],
    "whyWorkWithMe": [...],
    "callToAction": {...}
  },
  "similarity_score": 0.8234,
  "metadata": {
    "document_id": "507f1f77bcf86cd799439011",
    "threshold_used": 0.7,
    "total_documents_searched": 5,
    "match_index": 1
  }
}
```

**No Match Response (404):**
```json
{
  "error": "No matching data found.",
  "details": {
    "best_similarity": 0.4521,
    "threshold_used": 0.6,
    "total_documents_searched": 5
  }
}
```

### Batch Query
```http
POST /query/batch
Content-Type: application/json
```

**Request:**
```json
{
  "questions": [
    "What is machine learning?",
    "How do I deploy models?"
  ],
  "threshold": 0.6,
  "top_k": 2
}
```

**Response:**
```json
{
  "results": [
    {
      "question_index": 0,
      "query": "What is machine learning?",
      "matches": [
        {
          "matched_question": "What is machine learning?",
          "answers": {...},
          "similarity_score": 0.9876,
          "document_id": "507f1f77bcf86cd799439011"
        }
      ]
    }
  ],
  "metadata": {
    "total_questions": 2,
    "total_documents_searched": 5,
    "threshold_used": 0.6,
    "top_k": 2
  }
}
```

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl http://localhost:5001/health

# Single query
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deep learning?"}'

# Query with custom threshold
curl -X POST http://localhost:5001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How to prevent overfitting?", "threshold": 0.7}'

# Batch query
curl -X POST http://localhost:5001/query/batch \
  -H "Content-Type: application/json" \
  -d '{"questions": ["What is ML?", "How to deploy?"], "top_k": 2}'
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:5001"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Single query
query_data = {
    "question": "What is neural network?",
    "threshold": 0.7
}
response = requests.post(f"{BASE_URL}/query", json=query_data)
print(response.json())

# Batch query
batch_data = {
    "questions": ["What is AI?", "How to use transformers?"],
    "threshold": 0.6,
    "top_k": 2
}
response = requests.post(f"{BASE_URL}/query/batch", json=batch_data)
print(response.json())
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/sentence_transformer_db` | Yes |
| `MONGODB_DATABASE` | Database name | `sentence_transformer_db` | Yes |
| `MONGODB_COLLECTION` | Collection name | `qa_documents` | Yes |
| `MODEL_NAME` | Sentence transformer model | `all-MiniLM-L6-v2` | No |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | `0.6` | No |
| `FLASK_ENV` | Flask environment | `development` | No |
| `FLASK_PORT` | Server port | `5001` | No |
| `SECRET_KEY` | Flask secret key | Generated | Yes (Production) |

### MongoDB Document Structure

Your MongoDB documents must follow this exact structure:

```json
{
  "_id": "ObjectId or String",
  "question": "The question text for matching",
  "answers": {
    "title": "Professional title",
    "subtitle": "Specialization",
    "about": "Detailed description",
    "projects": [
      {
        "name": "Project name",
        "description": "Project description"
      }
    ],
    "whyWorkWithMe": [
      "Reason 1",
      "Reason 2" 
    ],
    "callToAction": {
      "message": "CTA message",
      "contact": "Contact information"
    }
  }
}
```

### Similarity Threshold Guide

- **0.8-1.0**: Very strict matching (only very similar questions)
- **0.6-0.8**: Moderate matching (recommended for most use cases)  
- **0.4-0.6**: Loose matching (may include somewhat related questions)
- **0.0-0.4**: Very loose matching (not recommended for production)

## 🚀 Deployment

### GitHub Secrets Required

Set these secrets in your GitHub repository:

- `REMOTE_HOST`: Your server IP address
- `REMOTE_USER`: SSH username  
- `SSH_PRIVATE_KEY`: SSH private key content

### Environment Variables on Server

Create a `.env` file on your server or use environment variables:

```bash
# On your server
echo "MONGODB_URI=your-production-mongodb-uri" > /opt/flask-app/.env
echo "SIMILARITY_THRESHOLD=0.6" >> /opt/flask-app/.env
echo "FLASK_ENV=production" >> /opt/flask-app/.env
```

### Automated Deployment

1. Push to `main` branch or trigger manually
2. GitHub Actions will automatically deploy the containerized application

## 🌐 Nginx Configuration

Use the provided `nginx-config.conf` for SSL-enabled reverse proxy setup.

## 📊 Monitoring & Debugging

### Health Monitoring

The comprehensive `/health` endpoint provides:
- Model loading status and dimensions
- Database connectivity and document count  
- Configuration validation
- Overall system health

### Logs

```bash
# Application logs (Docker)
docker logs st-flask-container

# Application logs (local)
tail -f logs/flask_app.log

# Debug mode
FLASK_DEBUG=True python run.py
```

### Common Issues

1. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB connectivity
   docker exec -it st-flask-container python -c "from pymongo import MongoClient; print(MongoClient('your-uri').admin.command('ismaster'))"
   ```

2. **Model Loading Issues**
   - Ensure sufficient memory (800MB+)
   - Check internet connectivity for model download
   - Verify model name in configuration

3. **No Matches Found**
   - Check similarity threshold (try lowering it)
   - Verify document structure in MongoDB
   - Review question similarity with existing data

## 🔍 Development

### Project Structure

The application follows clean architecture principles:

- **`app/__init__.py`**: Application factory with dependency injection
- **`app/config.py`**: Centralized configuration management
- **`app/database/`**: Database access layer with MongoDB operations
- **`app/models/`**: Business logic for sentence transformer operations
- **`app/api/`**: HTTP API layer with request/response handling
- **`app/utils/`**: Utility functions for similarity calculations

### Adding New Features

1. **New API Endpoints**: Add to `app/api/routes.py`
2. **Database Operations**: Extend `app/database/mongodb.py`
3. **Model Operations**: Extend `app/models/sentence_model.py`
4. **Utilities**: Add to `app/utils/`

### Testing

```bash
# Unit tests (add as needed)
python -m pytest tests/

# Integration tests
curl http://localhost:5001/health
```

## 📈 Performance

### Development vs Production

**Local Development (Flask dev server):**
- Single-threaded with auto-reload
- Shows development server warnings (normal)
- Best for debugging and development

**Production (Gunicorn WSGI server):**
- Multi-worker process handling
- Production-optimized performance
- No development server warnings

### Performance Metrics

- **Cold Start**: ~15-20 seconds (model loading)
- **Query Response**: ~100-300ms average
- **Batch Processing**: ~50ms per additional query
- **Memory Usage**: ~800MB (model + dependencies)
- **Concurrent Requests**: Supports multiple concurrent requests with Gunicorn workers

## 🛡️ Security

- Non-root container user
- Input validation and sanitization  
- Configurable similarity thresholds
- Environment-based configuration
- Error message sanitization
- Request timeout handling

## 📝 License

This refactored Flask application is production-ready with modular architecture. The MongoDB integration allows for dynamic content management while maintaining high performance through efficient embedding and similarity calculations. 