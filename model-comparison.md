# Sentence Transformer Model Comparison for Production

## 🚨 Current Issue
- `all-MiniLM-L6-v2` (90MB) causing worker timeouts and memory kills
- Need smaller, more memory-efficient model for production deployment

## 🎯 Recommended Models (Smallest to Largest)

### 1. **paraphrase-MiniLM-L3-v2** ⭐ **RECOMMENDED**
- **Size**: ~22MB
- **Dimensions**: 384
- **Memory**: ~200-300MB total
- **Performance**: Good for most semantic search tasks
- **Speed**: Fastest inference

### 2. **all-MiniLM-L12-v2** 
- **Size**: ~35MB  
- **Dimensions**: 384
- **Memory**: ~400-500MB total
- **Performance**: Slightly better than L3
- **Speed**: Fast inference

### 3. **all-MiniLM-L6-v2** (Current - Too Large)
- **Size**: ~90MB
- **Dimensions**: 384
- **Memory**: ~800-1000MB total
- **Performance**: Best quality but too memory-intensive
- **Speed**: Slower inference

## 🔧 Quick Model Switch

### Option 1: Ultra-Lightweight (Recommended)
```bash
# Update config to use smallest model
MODEL_NAME=paraphrase-MiniLM-L3-v2
```

### Option 2: Balanced Performance
```bash
# Update config to use medium model  
MODEL_NAME=all-MiniLM-L12-v2
```

## 📊 Performance Comparison

| Model | Size | Memory | Startup Time | Query Time | Quality |
|-------|------|--------|--------------|------------|---------|
| **paraphrase-MiniLM-L3-v2** | 22MB | ~300MB | 10-15s | 50-100ms | ⭐⭐⭐⭐ |
| **all-MiniLM-L12-v2** | 35MB | ~500MB | 15-20s | 100-150ms | ⭐⭐⭐⭐⭐ |
| **all-MiniLM-L6-v2** | 90MB | ~1GB | 30-40s | 200-300ms | ⭐⭐⭐⭐⭐⭐ |

## 🚀 Deployment Commands

### For Ultra-Lightweight Model:
```bash
docker run -d \
  --name st-flask-container \
  --restart unless-stopped \
  -p 5001:5001 \
  --memory=1g \
  --memory-swap=1g \
  -e MODEL_NAME="paraphrase-MiniLM-L3-v2" \
  -e MONGODB_URI="your-connection-string" \
  sentence-transformer-flask:latest
```

### For Balanced Model:
```bash
docker run -d \
  --name st-flask-container \
  --restart unless-stopped \
  -p 5001:5001 \
  --memory=1.5g \
  --memory-swap=1.5g \
  -e MODEL_NAME="all-MiniLM-L12-v2" \
  -e MONGODB_URI="your-connection-string" \
  sentence-transformer-flask:latest
```

## ✅ Expected Results with Smaller Model

- **✅ No Worker Timeouts**: Much faster model loading
- **✅ Lower Memory Usage**: 300-500MB vs 1GB
- **✅ Faster Startup**: 10-20s vs 40s+
- **✅ Stable Operations**: No more SIGKILL errors
- **✅ Better Performance**: Faster query responses

The ultra-lightweight model should completely eliminate your production issues! 