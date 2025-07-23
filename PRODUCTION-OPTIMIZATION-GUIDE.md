# 🚀 Production Optimization Guide for Sentence Transformer API

## 📊 **System Requirements & Recommendations**

### **Your Hardware (3 vCPU, 8GB RAM)**
- **Optimal Configuration**: ✅ Perfect for this setup
- **Recommended Workers**: 3 workers (1 worker per vCPU)
- **Memory Allocation**: ~1.5GB per worker + 2GB system overhead
- **Expected Peak Usage**: 6GB RAM, 80-90% CPU during inference

### **Resource Formula**
```
Workers = min(CPU_cores, (Total_RAM - 2GB) / 1.5GB)
For 8GB RAM: (8-2)/1.5 = 4 workers max, but use 3 for stability
```

## 🛠️ **Optimized Configurations**

### **1. Gunicorn Configuration** (`gunicorn-production.conf.py`)

**Key Optimizations:**
- **Workers**: 3 (matches your vCPUs)
- **Timeout**: 120s (reasonable for production)
- **Worker Lifecycle**: Restart after 50 requests to prevent memory leaks
- **Preload App**: Share model across workers

```python
workers = 3                    # Perfect for 3 vCPU
timeout = 120                  # Reasonable production timeout
max_requests = 50              # Restart workers frequently
worker_tmp_dir = "/dev/shm"    # Use shared memory
preload_app = True             # Share model loading
```

### **2. Docker Resource Limits** (`docker-compose.production.yml`)

**Critical Settings:**
```yaml
deploy:
  resources:
    limits:
      memory: 6G        # Leave 2GB for system
      cpus: '2.5'       # Leave 0.5 CPU for system
    reservations:
      memory: 2G        # Minimum required
      cpus: '1.0'       # Minimum required
```

### **3. Model Optimization** (`sentence_model_optimized.py`)

**Key Features:**
- **Aggressive Memory Cleanup**: Force garbage collection after each request
- **Float32 Precision**: Reduce memory usage by 50%
- **Batch Size Limit**: Maximum 4 items per batch
- **Thread Limiting**: 2 PyTorch threads for memory efficiency

## 🚨 **Common Issues & Solutions**

### **Issue 1: Worker Timeouts**

**Symptoms:**
```
[CRITICAL] WORKER TIMEOUT (pid:1234)
worker 1 killed (signal 9)
```

**Solutions:**
```bash
# 1. Check if model is downloading multiple formats
docker logs container_name | grep -i "download"

# 2. Verify environment variables are set
docker exec container_name env | grep SENTENCE_TRANSFORMERS

# 3. Monitor memory during startup
./monitor-resources.sh monitor
```

**Root Causes:**
- Model downloading ONNX/OpenVINO formats (400MB+ extra)
- Insufficient timeout for first request
- Memory pressure causing worker kills

### **Issue 2: Out of Memory (OOM)**

**Symptoms:**
```
worker sent SIGKILL "Perhaps out of memory"
MemoryError: Unable to allocate array
```

**Solutions:**
```bash
# 1. Reduce workers temporarily
docker-compose down
# Edit gunicorn config: workers = 2
docker-compose up -d

# 2. Check system memory
free -h
df -h

# 3. Monitor container memory
docker stats container_name
```

### **Issue 3: Slow API Responses**

**Solutions:**
```bash
# 1. Check if model loads on each request (bad)
docker logs container_name | grep "Loading model"

# 2. Monitor CPU usage
./monitor-resources.sh check

# 3. Test with smaller batch sizes
curl -X POST -H "Content-Type: application/json" \
  -d '{"questions": ["test"]}' \
  http://localhost:5001/query/batch
```

## 📋 **Deployment Steps**

### **1. Quick Deployment**
```bash
# Make scripts executable
chmod +x deploy-production.sh monitor-resources.sh

# Deploy with resource checking
./deploy-production.sh
```

### **2. Manual Deployment**
```bash
# Build optimized image
docker build -f Dockerfile.production-optimized -t sentence-api .

# Deploy with resource limits
docker-compose -f docker-compose.production.yml up -d

# Monitor startup
./monitor-resources.sh monitor
```

### **3. Health Verification**
```bash
# Check comprehensive health
curl -s http://localhost:5001/health | jq .

# Test API functionality
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}' \
  http://localhost:5001/query

# Monitor resources
docker stats --no-stream
```

## 📊 **Monitoring & Troubleshooting**

### **Resource Monitoring**
```bash
# Continuous monitoring
./monitor-resources.sh monitor

# Quick health check
./monitor-resources.sh check

# Generate detailed report
./monitor-resources.sh report
```

### **Key Metrics to Watch**

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Memory Usage | <70% | 70-85% | >85% |
| CPU Usage | <80% | 80-95% | >95% |
| Response Time | <2s | 2-5s | >5s |
| Worker Restarts | <5/hour | 5-20/hour | >20/hour |

### **Log Analysis**
```bash
# View recent errors
docker logs sentence-transformer-api 2>&1 | grep -i error

# Monitor worker lifecycle
docker logs sentence-transformer-api 2>&1 | grep -i worker

# Check model loading
docker logs sentence-transformer-api 2>&1 | grep -i "model"
```

## ⚡ **Performance Optimization Tips**

### **1. Model Optimization**
- **Use smallest model**: `paraphrase-MiniLM-L3-v2` (22MB)
- **Disable unused formats**: Set `SENTENCE_TRANSFORMERS_DISABLE_ONNX=1`
- **CPU-only mode**: No CUDA overhead
- **Float32 precision**: 50% memory reduction

### **2. System Optimization**
```bash
# Increase file descriptors
ulimit -n 65536

# Use shared memory for temporary files
# Already configured in worker_tmp_dir = "/dev/shm"

# Optimize malloc behavior
export MALLOC_TRIM_THRESHOLD_=100000
```

### **3. Docker Optimization**
```dockerfile
# Use multi-stage builds
FROM python:3.10-slim

# Aggressive cleanup
RUN pip cache purge && rm -rf /root/.cache/pip/* /tmp/*

# Resource limits
shm_size: 1G
ulimits:
  memlock: -1
  nofile:
    soft: 65536
    hard: 65536
```

## 🔧 **Troubleshooting Commands**

### **Emergency Actions**
```bash
# Restart service quickly
docker-compose -f docker-compose.production.yml restart

# Check container status
docker ps -a

# View last 50 log lines
docker logs sentence-transformer-api --tail=50

# Kill and recreate if stuck
docker-compose -f docker-compose.production.yml down --remove-orphans
docker-compose -f docker-compose.production.yml up -d
```

### **Resource Investigation**
```bash
# Container resource usage
docker stats sentence-transformer-api --no-stream

# System resource usage
htop
free -h
df -h

# Process tree
ps aux | grep gunicorn
```

### **Model Investigation**
```bash
# Check model cache size
du -sh model-cache/
du -sh huggingface-cache/

# List downloaded files
find model-cache/ -type f -name "*.bin" -o -name "*.safetensors"

# Check environment variables
docker exec sentence-transformer-api env | grep -E "(SENTENCE|HF|TRANSFORM)"
```

## 🎯 **Expected Performance**

### **Startup Time**
- **Cold Start**: 60-120 seconds (model download + loading)
- **Warm Start**: 10-30 seconds (model loading only)
- **Hot Restart**: 5-10 seconds (cached model)

### **Runtime Performance**
- **Single Query**: 100-500ms
- **Batch Query (5 items)**: 200-800ms
- **Memory Usage**: 1.2-1.8GB per worker
- **CPU Usage**: 30-80% during inference

### **Scaling Guidelines**

| Server Size | Workers | Max Memory | Expected QPS |
|-------------|---------|------------|--------------|
| 4GB RAM | 1-2 | 3GB | 5-10 |
| 8GB RAM | 2-3 | 6GB | 10-20 |
| 16GB RAM | 4-6 | 12GB | 20-40 |

## 🏆 **Success Indicators**

✅ **Healthy Service:**
- Health check returns 200 OK
- Memory usage stable <70%
- Workers restart <5 times/hour
- API responses <2 seconds
- No timeout errors in logs

❌ **Problematic Service:**
- Frequent worker timeouts
- Memory usage >85%
- API errors or 5xx responses
- Response times >5 seconds
- Continuous worker cycling

This guide should resolve your worker timeout and OOM issues while maximizing performance on your 8GB server! 🚀 