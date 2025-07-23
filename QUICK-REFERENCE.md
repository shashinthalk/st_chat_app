# 🚀 Quick Reference - Production Deployment Commands

## **Immediate Deployment (Recommended)**

```bash
# 1. One-command deployment with monitoring
./deploy-production.sh

# 2. Monitor resources in real-time
./monitor-resources.sh monitor

# 3. Check health status
curl -s http://localhost:5001/health | jq .
```

## **Docker Run Commands (Alternative to docker-compose)**

### **Production Docker Run**
```bash
docker run -d \
  --name sentence-transformer-api \
  --restart unless-stopped \
  -p 5001:5001 \
  --memory=6g \
  --cpus=2.5 \
  --shm-size=1g \
  --ulimit memlock=-1 \
  --ulimit nofile=65536:65536 \
  --ulimit stack=67108864 \
  -e FLASK_ENV=production \
  -e MODEL_NAME=paraphrase-MiniLM-L3-v2 \
  -e SIMILARITY_THRESHOLD=0.6 \
  -e MONGODB_URI="mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/" \
  -e MONGODB_DATABASE=automation_with_ai_data \
  -e MONGODB_COLLECTION=knowledge_base \
  -e SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers \
  -e HF_HOME=/tmp/huggingface \
  -e TRANSFORMERS_CACHE=/tmp/transformers_cache \
  -e SENTENCE_TRANSFORMERS_DISABLE_ONNX=1 \
  -e SENTENCE_TRANSFORMERS_DISABLE_OPENVINO=1 \
  -e MALLOC_TRIM_THRESHOLD_=100000 \
  -e PYTHONUNBUFFERED=1 \
  -e PYTHONDONTWRITEBYTECODE=1 \
  -v $(pwd)/logs:/app/logs \
  -v sentence-model-cache:/tmp/sentence_transformers \
  -v huggingface-cache:/tmp/huggingface \
  sentence-transformer-api:latest
```

### **Memory-Constrained Run (Conservative)**
```bash
docker run -d \
  --name sentence-transformer-api-safe \
  --restart unless-stopped \
  -p 5001:5001 \
  --memory=4g \
  --cpus=2.0 \
  --shm-size=512m \
  -e FLASK_ENV=production \
  -e MODEL_NAME=paraphrase-MiniLM-L3-v2 \
  -e MONGODB_URI="mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/" \
  -e MONGODB_DATABASE=automation_with_ai_data \
  -e MONGODB_COLLECTION=knowledge_base \
  -e SENTENCE_TRANSFORMERS_DISABLE_ONNX=1 \
  -e SENTENCE_TRANSFORMERS_DISABLE_OPENVINO=1 \
  -v $(pwd)/logs:/app/logs \
  sentence-transformer-api:latest
```

## **Build Commands**

```bash
# Build production-optimized image
docker build -f Dockerfile.production-optimized -t sentence-transformer-api:latest .

# Build with alternative requirements (if build fails)
docker build -f Dockerfile.production-optimized \
  --build-arg REQUIREMENTS_FILE=requirements-production.txt \
  -t sentence-transformer-api:latest .
```

## **Monitoring Commands**

```bash
# Real-time monitoring
./monitor-resources.sh monitor

# Quick status check
./monitor-resources.sh check

# View logs with error highlighting  
./monitor-resources.sh logs

# Generate detailed report
./monitor-resources.sh report

# Docker stats
docker stats sentence-transformer-api --no-stream

# Memory usage breakdown
docker exec sentence-transformer-api ps aux
```

## **API Testing Commands**

```bash
# Health check
curl -f http://localhost:5001/health

# Single query test
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}' \
  http://localhost:5001/query

# Batch query test
curl -X POST -H "Content-Type: application/json" \
  -d '{"questions": ["What is AI?", "How does ML work?"], "top_k": 2}' \
  http://localhost:5001/query/batch

# Performance test (load testing)
for i in {1..10}; do
  curl -X POST -H "Content-Type: application/json" \
    -d '{"question": "test query '$i'"}' \
    http://localhost:5001/query &
done
wait
```

## **Troubleshooting Commands**

### **Container Issues**
```bash
# Check container status
docker ps -a | grep sentence

# View recent logs
docker logs sentence-transformer-api --tail=50 --follow

# Get container resource usage
docker stats sentence-transformer-api

# Execute commands inside container
docker exec -it sentence-transformer-api /bin/bash

# Check environment variables
docker exec sentence-transformer-api env | grep -E "(SENTENCE|HF|TRANSFORM)"
```

### **Memory Issues**
```bash
# Check system memory
free -h

# Check Docker memory usage
docker system df

# Clean up Docker resources
docker system prune -a --volumes

# Check container memory limit
docker inspect sentence-transformer-api | grep -i memory
```

### **Worker Issues**
```bash
# Check Gunicorn workers
docker exec sentence-transformer-api ps aux | grep gunicorn

# Restart container
docker restart sentence-transformer-api

# View Gunicorn config
docker exec sentence-transformer-api cat gunicorn.conf.py
```

## **Performance Tuning**

### **For Lower Memory (4-6GB systems)**
```bash
# Use conservative Gunicorn config
cat > gunicorn-conservative.conf.py << 'EOF'
workers = 2
timeout = 180
max_requests = 30
worker_tmp_dir = "/dev/shm"
preload_app = True
EOF

# Deploy with conservative settings
docker run ... -v $(pwd)/gunicorn-conservative.conf.py:/app/gunicorn.conf.py ...
```

### **For Higher Performance (16GB+ systems)**
```bash
# Use aggressive Gunicorn config
cat > gunicorn-aggressive.conf.py << 'EOF'
workers = 6
timeout = 60
max_requests = 100
worker_tmp_dir = "/dev/shm"
preload_app = True
worker_connections = 200
EOF
```

## **Environment Variables Reference**

### **Required**
```bash
MONGODB_URI=mongodb+srv://user:pass@host/
MONGODB_DATABASE=your_database
MONGODB_COLLECTION=your_collection
```

### **Model Optimization (Critical)**
```bash
MODEL_NAME=paraphrase-MiniLM-L3-v2
SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers
HF_HOME=/tmp/huggingface
TRANSFORMERS_CACHE=/tmp/transformers_cache
SENTENCE_TRANSFORMERS_DISABLE_ONNX=1
SENTENCE_TRANSFORMERS_DISABLE_OPENVINO=1
```

### **Memory Optimization**
```bash
MALLOC_TRIM_THRESHOLD_=100000
MALLOC_TOP_PAD_=100000
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

## **Expected Resource Usage**

### **Your 8GB Server**
| Phase | CPU % | Memory GB | Duration |
|-------|-------|-----------|----------|
| Startup | 50-80% | 0.5-2.0 | 60-120s |
| Idle | 5-15% | 1.5-2.5 | - |
| Query Processing | 40-90% | 2.0-4.0 | 100-500ms |
| Batch Processing | 60-95% | 3.0-5.0 | 500ms-2s |

### **Success Metrics**
- ✅ **Startup**: Complete in <2 minutes
- ✅ **Memory**: Stable at <70% (5.6GB)
- ✅ **Response**: <2 seconds per query
- ✅ **Workers**: <5 restarts per hour
- ✅ **Health**: Returns 200 OK consistently

## **Emergency Recovery**

```bash
# Complete service reset
docker-compose -f docker-compose.production.yml down --remove-orphans
docker system prune -f
docker volume prune -f
./deploy-production.sh

# If deployment script fails, manual reset:
docker stop sentence-transformer-api
docker rm sentence-transformer-api
docker rmi sentence-transformer-api:latest
docker build -f Dockerfile.production-optimized -t sentence-transformer-api:latest .
# Then run docker run command from above
```

This quick reference should get your service running optimally on your 8GB server! 🎯 