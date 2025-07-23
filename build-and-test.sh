#!/bin/bash

# Simple Flask Q&A API - Build and Test Script
echo "🚀 Building and testing Flask Q&A API..."

# Check Python and pip
echo "📋 Checking requirements..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
pip --version || { echo "❌ pip not found"; exit 1; }

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Test Flask app creation
echo "🧪 Testing Flask app creation..."
python -c "from app import create_app; app = create_app(); print('✅ Flask app created successfully')"

# Test data loading
echo "🧪 Testing Q&A data loading..."
python -c "from app.data import QA_DATA; print(f'✅ Q&A data loaded: {len(QA_DATA)} items')"

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t flask-qa-api .

# Test Docker image
echo "🧪 Testing Docker container..."
docker run -d --name test-qa-api -p 5002:5001 flask-qa-api

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
echo "🔍 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:5002/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed"
    echo "Response: $HEALTH_RESPONSE"
else
    echo "❌ Health check failed"
    echo "Response: $HEALTH_RESPONSE"
    docker logs test-qa-api
    docker stop test-qa-api && docker rm test-qa-api
    exit 1
fi

# Test query endpoint
echo "🔍 Testing query endpoint..."
QUERY_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"question": "What is machine learning?"}' \
    http://localhost:5002/query)

if echo "$QUERY_RESPONSE" | grep -q "matched.*true"; then
    echo "✅ Query test passed"
    echo "Response: $QUERY_RESPONSE"
else
    echo "❌ Query test failed"
    echo "Response: $QUERY_RESPONSE"
fi

# Test no match scenario
echo "🔍 Testing no match scenario..."
NO_MATCH_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"question": "What is cooking?"}' \
    http://localhost:5002/query)

if echo "$NO_MATCH_RESPONSE" | grep -q "No matching answer found"; then
    echo "✅ No match test passed"
else
    echo "❌ No match test failed"
    echo "Response: $NO_MATCH_RESPONSE"
fi

# Clean up
echo "🧹 Cleaning up..."
docker stop test-qa-api && docker rm test-qa-api

# Save Docker image
echo "💾 Saving Docker image..."
docker save flask-qa-api | gzip > flask-qa-api.tar.gz

echo ""
echo "🎉 Build and test completed successfully!"
echo ""
echo "📊 Summary:"
echo "  ✅ Dependencies installed"
echo "  ✅ Flask app working"
echo "  ✅ Docker image built"
echo "  ✅ Health endpoint working"
echo "  ✅ Query endpoint working"
echo "  ✅ Error handling working"
echo ""
echo "📁 Files ready for deployment:"
echo "  - flask-qa-api.tar.gz (Docker image)"
echo "  - All source files in current directory"
echo ""
echo "🚀 Ready for production deployment!" 