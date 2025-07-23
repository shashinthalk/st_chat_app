#!/bin/bash

# Production Deployment Script for Sentence Transformer API
# Optimized for 3 vCPU, 8GB RAM server

set -e

echo "🚀 Starting production deployment for Sentence Transformer API"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="sentence-transformer-api"
CONTAINER_NAME="sentence-api-prod"
HEALTH_CHECK_URL="http://localhost:5001/health"
MAX_WAIT_TIME=300  # 5 minutes

# Check system resources
echo -e "${YELLOW}📊 Checking system resources...${NC}"
echo "CPU Cores: $(nproc)"
echo "Total Memory: $(free -h | awk '/^Mem/ {print $2}')"
echo "Available Memory: $(free -h | awk '/^Mem/ {print $7}')"
echo "Disk Space: $(df -h / | awk 'NR==2 {print $4}')"

# Ensure minimum requirements
TOTAL_MEM_GB=$(free -g | awk '/^Mem/ {print $2}')
if [ "$TOTAL_MEM_GB" -lt 6 ]; then
    echo -e "${RED}❌ Insufficient memory! Need at least 6GB, found ${TOTAL_MEM_GB}GB${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p model-cache
mkdir -p huggingface-cache

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}🔧 Creating .env file template...${NC}"
    cat > .env << EOF
MONGODB_URI=mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/
MONGODB_DATABASE=automation_with_ai_data
MONGODB_COLLECTION=knowledge_base
FLASK_ENV=production
MODEL_NAME=paraphrase-MiniLM-L3-v2
SIMILARITY_THRESHOLD=0.6
EOF
    echo -e "${GREEN}✅ Created .env file - please update with your credentials${NC}"
fi

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.production.yml down --remove-orphans || true
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Build optimized image
echo -e "${YELLOW}🏗️ Building production-optimized Docker image...${NC}"
docker build -f Dockerfile.production-optimized -t $IMAGE_NAME:latest .

# Check image size
IMAGE_SIZE=$(docker images $IMAGE_NAME:latest --format "table {{.Size}}" | tail -1)
echo -e "${GREEN}📦 Built image size: $IMAGE_SIZE${NC}"

# Start with docker-compose for better resource management
echo -e "${YELLOW}🚀 Starting production services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏱️ Waiting for services to be healthy...${NC}"
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT_TIME ]; do
    if curl -f $HEALTH_CHECK_URL >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 5
    WAIT_TIME=$((WAIT_TIME + 5))
done

if [ $WAIT_TIME -ge $MAX_WAIT_TIME ]; then
    echo -e "${RED}❌ Service failed to become healthy within $MAX_WAIT_TIME seconds${NC}"
    echo "Checking logs..."
    docker-compose -f docker-compose.production.yml logs --tail=50
    exit 1
fi

# Run health check and display results
echo -e "${YELLOW}🔍 Running comprehensive health check...${NC}"
HEALTH_RESPONSE=$(curl -s $HEALTH_CHECK_URL | jq '.' 2>/dev/null || curl -s $HEALTH_CHECK_URL)
echo "Health Check Response:"
echo "$HEALTH_RESPONSE"

# Display resource usage
echo -e "${YELLOW}📊 Current resource usage:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"

# Test API functionality
echo -e "${YELLOW}🧪 Testing API functionality...${NC}"
TEST_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "test query for deployment"}' \
    http://localhost:5001/query)

if echo "$TEST_RESPONSE" | grep -q "error"; then
    echo -e "${YELLOW}⚠️ API test returned error (expected for test query):${NC}"
    echo "$TEST_RESPONSE" | jq '.' 2>/dev/null || echo "$TEST_RESPONSE"
else
    echo -e "${GREEN}✅ API test successful:${NC}"
    echo "$TEST_RESPONSE" | jq '.' 2>/dev/null || echo "$TEST_RESPONSE"
fi

# Display final status
echo -e "${GREEN}🎉 Production deployment completed successfully!${NC}"
echo ""
echo "📍 Service URLs:"
echo "  - Health Check: $HEALTH_CHECK_URL"
echo "  - API Endpoint: http://localhost:5001/query"
echo "  - Nginx Proxy: http://localhost:80 (if enabled)"
echo ""
echo "📊 Monitoring commands:"
echo "  - View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  - Monitor resources: docker stats"
echo "  - Check health: curl $HEALTH_CHECK_URL"
echo ""
echo "🛠️ Management commands:"
echo "  - Stop services: docker-compose -f docker-compose.production.yml down"
echo "  - Restart services: docker-compose -f docker-compose.production.yml restart"
echo "  - View container logs: docker logs sentence-transformer-api" 