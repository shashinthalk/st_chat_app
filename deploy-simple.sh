#!/bin/bash

# Simple Flask Q&A API - Manual Deployment Script
echo "🚀 Deploying Flask Q&A API..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="flask-qa-api"
CONTAINER_NAME="flask-qa-container"
HEALTH_CHECK_URL="http://localhost:5001/health"
MAX_WAIT_TIME=60  # 1 minute

# Build the Docker image
echo -e "${YELLOW}🏗️ Building Docker image...${NC}"
docker build -t $IMAGE_NAME:latest .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Stop and remove existing container
echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || echo "No existing container to stop"
docker rm $CONTAINER_NAME 2>/dev/null || echo "No existing container to remove"

# Run the new container
echo -e "${YELLOW}🚀 Starting new container...${NC}"
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -p 5001:5001 \
  $IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

# Wait for container to be healthy
echo -e "${YELLOW}⏱️ Waiting for service to be ready...${NC}"
WAIT_TIME=0
while [ $WAIT_TIME -lt $MAX_WAIT_TIME ]; do
    if curl -f -s $HEALTH_CHECK_URL >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
done

if [ $WAIT_TIME -ge $MAX_WAIT_TIME ]; then
    echo -e "${RED}❌ Service failed to become healthy within $MAX_WAIT_TIME seconds${NC}"
    echo "Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Run comprehensive tests
echo -e "${YELLOW}🔍 Running deployment tests...${NC}"

# Test health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s $HEALTH_CHECK_URL)
echo "Health response: $HEALTH_RESPONSE"

# Test query endpoint
echo "Testing query endpoint..."
QUERY_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}' \
  http://localhost:5001/query)
echo "Query response: $QUERY_RESPONSE"

# Test AI synonym matching
echo "Testing AI synonym matching..."
AI_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}' \
  http://localhost:5001/query)
echo "AI query response: $AI_RESPONSE"

# Test no match scenario
echo "Testing no match scenario..."
NO_MATCH_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"question": "What is cooking?"}' \
  http://localhost:5001/query)
echo "No match response: $NO_MATCH_RESPONSE"

# Show container status
echo -e "${YELLOW}📊 Container status:${NC}"
docker ps | grep $CONTAINER_NAME

# Show resource usage
echo -e "${YELLOW}📊 Resource usage:${NC}"
docker stats $CONTAINER_NAME --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo "📍 Service URLs:"
echo "  - Health Check: $HEALTH_CHECK_URL"
echo "  - API Endpoint: http://localhost:5001/query"
echo ""
echo "📊 Management commands:"
echo "  - View logs: docker logs $CONTAINER_NAME"
echo "  - Stop service: docker stop $CONTAINER_NAME"
echo "  - Restart service: docker restart $CONTAINER_NAME"
echo ""
echo "🧪 Test commands:"
echo "  - Health: curl $HEALTH_CHECK_URL"
echo "  - Query: curl -X POST -H 'Content-Type: application/json' -d '{\"question\": \"What is AI?\"}' http://localhost:5001/query" 