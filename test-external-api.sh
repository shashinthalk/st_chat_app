#!/bin/bash

# Test script for external API integration
echo "🧪 Testing Flask Q&A API with External Knowledge Base"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_BASE="http://localhost:5001"

echo -e "${BLUE}📍 Testing Flask API with External Knowledge Base Integration${NC}"
echo ""

# Test 1: Health endpoint
echo -e "${YELLOW}💚 Test 1: Health endpoint with knowledge base status${NC}"
echo "Request: GET $API_BASE/health"
response=$(curl -s -w "\n%{http_code}" $API_BASE/health)
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

# Test 2: Cache info endpoint
echo -e "${YELLOW}📊 Test 2: Cache information endpoint${NC}"
echo "Request: GET $API_BASE/cache/info"
response=$(curl -s -w "\n%{http_code}" $API_BASE/cache/info)
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

# Test 3: Query - Kotlin development
echo -e "${YELLOW}⚡ Test 3: Query - Kotlin development${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "can u develop kotlin api backend"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "can u develop kotlin api backend"}' \
    $API_BASE/query)
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

# Test 4: Query - About yourself
echo -e "${YELLOW}👤 Test 4: Query - About yourself${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "tell me about yourself"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "tell me about yourself"}' \
    $API_BASE/query)
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

# Test 5: Query - Education and career
echo -e "${YELLOW}🎓 Test 5: Query - Education and career${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "education and career experience"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "education and career experience"}' \
    $API_BASE/query)
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

# Test 6: Query - No match scenario
echo -e "${YELLOW}🔍 Test 6: Query - No match scenario${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "What is cooking?"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "What is cooking?"}' \
    $API_BASE/query)
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

# Test 7: Clear cache
echo -e "${YELLOW}🗑️ Test 7: Clear cache${NC}"
echo "Request: POST $API_BASE/cache/clear"
response=$(curl -s -w "\n%{http_code}" -X POST $API_BASE/cache/clear)
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

# Test 8: Direct external API test
echo -e "${YELLOW}🌐 Test 8: Testing external API directly${NC}"
echo "Request: GET https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data"
external_response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer a>6rj{pvGUpdaZfy$(#2Ss)" https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data)
external_http_code=$(echo "$external_response" | tail -n1)
external_body=$(echo "$external_response" | head -n -1)

if [[ "$external_http_code" == "200" ]]; then
    echo -e "${GREEN}✅ External API Status: $external_http_code${NC}"
    echo "Response Preview (first 500 chars):"
    echo "$external_body" | head -c 500
    echo ""
    echo "Total items: $(echo "$external_body" | jq length 2>/dev/null || echo "Unable to count")"
else
    echo -e "${RED}❌ External API Status: $external_http_code${NC}"
    echo "Response: $external_body"
fi
echo ""

# Summary
echo -e "${BLUE}📊 Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Local API: $API_BASE"
echo "External API: https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data"
echo "Timestamp: $(date)"
echo ""
echo -e "${GREEN}✅ External API integration testing completed${NC}"
echo ""
echo -e "${BLUE}💡 Usage Examples:${NC}"
echo ""
echo "# Health check with knowledge base status"
echo "curl $API_BASE/health"
echo ""
echo "# Ask about Kotlin development"
echo "curl -X POST -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"can u develop kotlin api backend\"}' \\"
echo "  $API_BASE/query"
echo ""
echo "# Ask about personal background"
echo "curl -X POST -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"tell me about yourself\"}' \\"
echo "  $API_BASE/query" 