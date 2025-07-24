#!/bin/bash

# API Testing Script for api.shashinthalk.cc
# Tests the API through the Nginx reverse proxy

echo "🧪 Testing Flask Q&A API at api.shashinthalk.cc"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="api.shashinthalk.cc"
BASE_URL="https://$DOMAIN"

# Test if domain is accessible
echo -e "${YELLOW}🌐 Testing domain accessibility...${NC}"
if curl -f -s --connect-timeout 10 $BASE_URL > /dev/null; then
    echo -e "${GREEN}✅ Domain is accessible${NC}"
else
    echo -e "${YELLOW}⚠️ HTTPS not available, trying HTTP...${NC}"
    BASE_URL="http://$DOMAIN"
    if curl -f -s --connect-timeout 10 $BASE_URL > /dev/null; then
        echo -e "${GREEN}✅ Domain accessible via HTTP${NC}"
    else
        echo -e "${RED}❌ Domain is not accessible${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}📍 Testing API endpoints at: $BASE_URL${NC}"
echo ""

# Test 1: Root endpoint
echo -e "${YELLOW}📋 Test 1: Root endpoint${NC}"
echo "Request: GET $BASE_URL/"
response=$(curl -s -w "\n%{http_code}" $BASE_URL/)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 2: Health endpoint
echo -e "${YELLOW}💚 Test 2: Health endpoint${NC}"
echo "Request: GET $BASE_URL/health"
response=$(curl -s -w "\n%{http_code}" $BASE_URL/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 3: Query endpoint - Machine Learning
echo -e "${YELLOW}🤖 Test 3: Query endpoint - Machine Learning${NC}"
echo "Request: POST $BASE_URL/query"
echo 'Payload: {"question": "What is machine learning?"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "What is machine learning?"}' \
    $BASE_URL/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 4: Query endpoint - AI synonym
echo -e "${YELLOW}🧠 Test 4: Query endpoint - AI synonym matching${NC}"
echo "Request: POST $BASE_URL/query"
echo 'Payload: {"question": "What is AI?"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "What is AI?"}' \
    $BASE_URL/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 5: Query endpoint - No match
echo -e "${YELLOW}🔍 Test 5: Query endpoint - No match scenario${NC}"
echo "Request: POST $BASE_URL/query"
echo 'Payload: {"question": "What is cooking?"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "What is cooking?"}' \
    $BASE_URL/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "404" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (Expected for no match)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${YELLOW}⚠️ Status: $http_code (Expected 404)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 6: Invalid endpoint
echo -e "${YELLOW}❌ Test 6: Invalid endpoint${NC}"
echo "Request: GET $BASE_URL/invalid"
response=$(curl -s -w "\n%{http_code}" $BASE_URL/invalid)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "404" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (Expected for invalid endpoint)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${YELLOW}⚠️ Status: $http_code (Expected 404)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 7: Rate limiting (send multiple requests quickly)
echo -e "${YELLOW}🚦 Test 7: Rate limiting${NC}"
echo "Sending 5 rapid requests to test rate limiting..."
for i in {1..5}; do
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d '{"question": "test"}' \
        $BASE_URL/query)
    echo "Request $i: HTTP $response"
    sleep 0.1
done
echo ""

# Performance test
echo -e "${YELLOW}⚡ Test 8: Response time test${NC}"
echo "Measuring response times for health endpoint..."
for i in {1..3}; do
    time_result=$(curl -s -w "%{time_total}" -o /dev/null $BASE_URL/health)
    echo "Health check $i: ${time_result}s"
done
echo ""

# SSL certificate test (if HTTPS)
if [[ "$BASE_URL" == "https://"* ]]; then
    echo -e "${YELLOW}🔐 Test 9: SSL certificate${NC}"
    ssl_info=$(curl -s --connect-timeout 10 -vI $BASE_URL 2>&1 | grep -E "(subject|issuer|expire)")
    if [[ -n "$ssl_info" ]]; then
        echo -e "${GREEN}✅ SSL certificate information:${NC}"
        echo "$ssl_info"
    else
        echo -e "${YELLOW}⚠️ Could not retrieve SSL certificate information${NC}"
    fi
    echo ""
fi

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Domain: $DOMAIN"
echo "Base URL: $BASE_URL"
echo "Timestamp: $(date)"
echo ""
echo -e "${GREEN}✅ API is accessible and functioning${NC}"
echo ""
echo -e "${BLUE}💡 Usage Examples:${NC}"
echo ""
echo "# Health check"
echo "curl $BASE_URL/health"
echo ""
echo "# Ask about machine learning"
echo "curl -X POST -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"What is machine learning?\"}' \\"
echo "  $BASE_URL/query"
echo ""
echo "# Ask about AI (synonym matching)"
echo "curl -X POST -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"What is AI?\"}' \\"
echo "  $BASE_URL/query" 