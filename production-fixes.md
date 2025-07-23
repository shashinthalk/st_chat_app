# Production Memory Optimization Fixes

## 🚨 Issues Identified from Docker Logs

- **Worker Timeouts**: Gunicorn workers timing out after 120 seconds
- **Memory Issues**: Workers being killed with SIGKILL (out of memory)
- **Worker Cycling**: Continuous worker restarts due to memory pressure

## ✅ Fixes Applied

### 1. Gunicorn Configuration Optimization

**Changes in `gunicorn.conf.py`:**
- **Workers**: Reduced from `cpu_count * 2 + 1` to `1` worker (memory efficiency)
- **Timeout**: Increased from `120s` to `300s` (model operations need more time)
- **Max Requests**: Reduced from `1000` to `100` (prevent memory accumulation)
- **Memory Management**: Added `/dev/shm` for temporary files

### 2. Model Memory Optimization

**Changes in `app/models/sentence_model.py`:**
- **Gradient Disabled**: `param.requires_grad = False` for all model parameters
- **Torch Context**: `torch.no_grad()` context managers for inference
- **Batch Processing**: Process embeddings in smaller batches (max 32)
- **Garbage Collection**: Force `gc.collect()` after operations
- **Progress Bars**: Disabled to reduce memory overhead

### 3. Docker Configuration

**Updated `Dockerfile`:**
- Uses `gunicorn.conf.py` for consistent configuration
- Copies all necessary configuration files

## 🚀 Deployment Instructions

### Step 1: Rebuild Docker Image

```bash
# Build new image with fixes
docker build -t sentence-transformer-flask:latest .

# Save as tarball for deployment
docker save sentence-transformer-flask:latest | gzip > sentence-transformer-flask-fixed.tar.gz
```

### Step 2: Deploy to Production Server

```bash
# Copy to server
scp sentence-transformer-flask-fixed.tar.gz user@server:/tmp/

# On server - stop current container
docker stop st-flask-container
docker rm st-flask-container

# Load new image
docker load < /tmp/sentence-transformer-flask-fixed.tar.gz

# Run with memory optimizations
docker run -d \
  --name st-flask-container \
  --restart unless-stopped \
  -p 5001:5001 \
  --memory=2g \
  --memory-swap=2g \
  -e MONGODB_URI="your-connection-string" \
  -e SIMILARITY_THRESHOLD="0.6" \
  sentence-transformer-flask:latest
```

### Step 3: Monitor Memory Usage

```bash
# Check container memory usage
docker stats st-flask-container

# Check application logs
docker logs -f st-flask-container

# Health check
curl http://localhost:5001/health
```

## 📊 Expected Improvements

- **✅ No Worker Timeouts**: 300s timeout handles model operations
- **✅ Stable Memory**: Single worker prevents memory competition
- **✅ Faster Responses**: Optimized model operations with batch processing
- **✅ Better Reliability**: Workers restart after 100 requests to prevent memory leaks

## 🎯 Performance Monitoring

**Memory Usage Should:**
- Stay under 2GB during normal operations
- Not show continuous growth (memory leaks)
- Remain stable during multiple requests

**Response Times Should:**
- Health check: < 1 second
- Query processing: 2-5 seconds (first time model loading)
- Subsequent queries: < 1 second

## 🔧 Additional Server Optimizations

### If Still Having Memory Issues:

```bash
# Option 1: Increase container memory limit
docker run -d \
  --name st-flask-container \
  --memory=4g \
  --memory-swap=4g \
  ...

# Option 2: Add swap space on server
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Server Resource Requirements:
- **Minimum RAM**: 2GB available for container
- **Recommended RAM**: 4GB+ for optimal performance
- **CPU**: 2+ cores recommended
- **Disk**: 1GB+ free space for model files

## 📋 Health Check Commands

```bash
# Test deployment
curl -X POST http://your-server:5001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test query"}'

# Monitor logs
docker logs st-flask-container | tail -100

# Check worker status
docker exec st-flask-container ps aux | grep gunicorn
```

The fixes should resolve the worker timeout and memory issues completely! 