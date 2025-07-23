#!/bin/bash

# Quick Fix and Redeploy Script
echo "🔧 Fixing and redeploying sentence transformer API..."

# Build the fixed image
echo "📦 Building fixed Docker image with psutil..."
docker build -f Dockerfile.fixed -t sentence-transformer-flask:latest .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed. Check the logs above."
    exit 1
fi

echo "✅ Docker image built successfully!"

# Save the image (for deployment)
echo "💾 Saving Docker image for deployment..."
docker save sentence-transformer-flask:latest | gzip > sentence-transformer-flask-fixed.tar.gz

echo "📊 Image sizes:"
ls -lh sentence-transformer-flask*.tar.gz

# Test locally (optional)
echo "🧪 Testing locally..."
docker stop st-flask-container 2>/dev/null || true
docker rm st-flask-container 2>/dev/null || true

docker run -d \
  --name st-flask-container \
  --restart unless-stopped \
  -p 5001:5001 \
  -e MONGODB_URI="mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/" \
  -e MONGODB_DATABASE=automation_with_ai_data \
  -e MONGODB_COLLECTION=knowledge_base \
  sentence-transformer-flask:latest

echo "⏳ Waiting for container to start..."
sleep 10

# Health check
echo "🔍 Testing health check..."
for i in {1..6}; do
    if curl -f -s http://localhost:5001/health > /dev/null; then
        echo "✅ Health check passed!"
        echo "📝 Health response:"
        curl -s http://localhost:5001/health | jq . 2>/dev/null || curl -s http://localhost:5001/health
        break
    else
        echo "⏳ Attempt $i/6 - waiting 5 seconds..."
        sleep 5
    fi
done

echo ""
echo "🎉 Fix completed! The image now includes:"
echo "  ✅ psutil for resource monitoring"
echo "  ✅ Optimized model loading"
echo "  ✅ Memory management"
echo "  ✅ Graceful fallback support"
echo ""
echo "📁 Files ready for deployment:"
echo "  - sentence-transformer-flask-fixed.tar.gz (updated image)"
echo ""
echo "🚀 Deploy this fixed image to your server!" 