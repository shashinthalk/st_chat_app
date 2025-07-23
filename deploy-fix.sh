#!/bin/bash

# Production Fix Deployment Script
# This script applies memory optimization fixes for the Flask API

set -e

echo "🔧 Applying Production Memory Optimization Fixes"

# Build new Docker image with fixes
echo "📦 Building optimized Docker image..."
docker build -t sentence-transformer-flask:latest .

# Save as tarball
echo "💾 Creating deployment tarball..."
docker save sentence-transformer-flask:latest | gzip > sentence-transformer-flask-fixed.tar.gz

echo "✅ Production fixes applied successfully!"
echo ""
echo "📋 Key Optimizations:"
echo "  ✓ Single worker for memory efficiency"
echo "  ✓ 300s timeout for model operations"
echo "  ✓ Memory cleanup with garbage collection"  
echo "  ✓ Batch processing for embeddings"
echo "  ✓ Torch no_grad context for inference"
echo ""
echo "🚀 To deploy to production server:"
echo "  1. Copy: scp sentence-transformer-flask-fixed.tar.gz user@server:/tmp/"
echo "  2. SSH to server and run:"
echo "     docker stop st-flask-container"
echo "     docker rm st-flask-container" 
echo "     docker load < /tmp/sentence-transformer-flask-fixed.tar.gz"
echo "     docker run -d --name st-flask-container --restart unless-stopped \\"
echo "       -p 5001:5001 --memory=2g --memory-swap=2g \\"
echo "       -e MONGODB_URI='your-connection-string' \\"
echo "       sentence-transformer-flask:latest"
echo ""
echo "📊 Monitor with: docker logs -f st-flask-container"
echo "🔍 Health check: curl http://localhost:5001/health" 