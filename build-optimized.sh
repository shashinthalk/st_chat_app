#!/bin/bash

echo "🚀 Docker Image Size Optimization Options"
echo "=========================================="
echo ""

# Option 1: Ultra-minimal build
echo "📦 Option 1: Ultra-Minimal Build (Recommended)"
echo "Expected size: ~800MB (vs 5.7GB current)"
echo "Build command:"
echo "  docker build -f Dockerfile.ultra-minimal -t st-flask:ultra-minimal ."
echo ""

# Option 2: Alpine-based build  
echo "📦 Option 2: Alpine-Based Build"
echo "Expected size: ~600MB"
echo "Build command:"
echo "  docker build -f Dockerfile.optimized -t st-flask:alpine ."
echo ""

# Option 3: Original with CPU-only PyTorch
echo "📦 Option 3: Original + CPU PyTorch"
echo "Expected size: ~2GB"
echo "Build command:"
echo "  docker build -t st-flask:cpu-only ."
echo ""

echo "🎯 Recommended deployment command:"
echo "docker run -d \\"
echo "  --name st-flask-container \\"
echo "  --restart unless-stopped \\"
echo "  -p 5001:5001 \\"
echo "  --memory=512m \\"
echo "  --memory-swap=512m \\"
echo "  -e MODEL_NAME='paraphrase-MiniLM-L3-v2' \\"
echo "  -e MONGODB_URI='your-connection-string' \\"
echo "  st-flask:ultra-minimal"
echo ""

# Size comparison
echo "📊 Size Comparison:"
echo "  Current:      5.7GB"
echo "  Ultra-minimal: ~800MB (86% reduction)"  
echo "  Alpine:       ~600MB (89% reduction)"
echo ""

# Build the ultra-minimal version
read -p "Build ultra-minimal image now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔨 Building ultra-minimal image..."
    docker build -f Dockerfile.ultra-minimal -t st-flask:ultra-minimal .
    echo "✅ Build complete!"
    echo "📏 Checking image size..."
    docker images st-flask:ultra-minimal
fi 