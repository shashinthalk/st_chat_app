#!/bin/bash

# Test script for AI transformer model integration
echo "🤖 Testing Flask Q&A API with AI Transformer Model Integration"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_BASE="http://localhost:5001"
TRANSFORMER_URL="http://95.111.228.138:5002/query"

echo -e "${BLUE}📍 Testing Flask API with AI Transformer Model${NC}"
echo ""

# Test 1: Health endpoint with AI model info
echo -e "${YELLOW}💚 Test 1: Health endpoint with AI model status${NC}"
echo "Request: GET $API_BASE/health"
response=$(curl -s -w "\n%{http_code}" $API_BASE/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
    
    # Extract dataset size
    dataset_size=$(echo "$body" | jq -r '.transformer_model.dataset_size' 2>/dev/null)
    echo -e "${BLUE}Dataset size: $dataset_size questions${NC}"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 2: Transformer model direct test
echo -e "${YELLOW}🤖 Test 2: Direct transformer model test${NC}"
echo "Request: GET $API_BASE/test-transformer"
response=$(curl -s -w "\n%{http_code}" $API_BASE/test-transformer)
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

# Test 3: Query with exact match
echo -e "${YELLOW}🎯 Test 3: Query with exact dataset question${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "can u develop kotlin api backend"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "can u develop kotlin api backend"}' \
    $API_BASE/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (Match found)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
elif [[ "$http_code" == "404" ]]; then
    echo -e "${YELLOW}⚠️ Status: $http_code (No match found by AI model)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 4: Query with similar question
echo -e "${YELLOW}🧠 Test 4: Query with similar question (AI matching)${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "what can you do with kotlin programming"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "what can you do with kotlin programming"}' \
    $API_BASE/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (AI model found match)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
elif [[ "$http_code" == "404" ]]; then
    echo -e "${YELLOW}⚠️ Status: $http_code (AI model found no confident match)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 5: Query about personal info
echo -e "${YELLOW}👤 Test 5: Query about personal information${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "who are you"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "who are you"}' \
    $API_BASE/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "200" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (AI model found match)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
elif [[ "$http_code" == "404" ]]; then
    echo -e "${YELLOW}⚠️ Status: $http_code (AI model found no confident match)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 6: Completely unrelated question
echo -e "${YELLOW}🔍 Test 6: Completely unrelated question${NC}"
echo "Request: POST $API_BASE/query"
echo 'Payload: {"question": "what is the weather today"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "what is the weather today"}' \
    $API_BASE/query)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" == "404" ]]; then
    echo -e "${GREEN}✅ Status: $http_code (Expected - no match for unrelated question)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
elif [[ "$http_code" == "200" ]]; then
    echo -e "${YELLOW}⚠️ Status: $http_code (Unexpected match found)${NC}"
    echo "Response: $body" | jq . 2>/dev/null || echo "Response: $body"
else
    echo -e "${RED}❌ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 7: Custom transformer test with specific question
echo -e "${YELLOW}🧪 Test 7: Custom transformer test${NC}"
echo "Request: POST $API_BASE/test-transformer"
echo 'Payload: {"question": "kotlin development"}'
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "kotlin development"}' \
    $API_BASE/test-transformer)
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

# Test 8: Direct transformer model test (bypassing Flask)
echo -e "${YELLOW}🌐 Test 8: Direct transformer model API test${NC}"
echo "Request: POST $TRANSFORMER_URL"

# Get dataset first
dataset_response=$(curl -s $API_BASE/cache/info)
echo "Getting dataset from Flask API..."

# Create test payload
test_payload='{
    "question": "kotlin backend development",
    "dataset": [
        "can u develop kotlin api backend",
        "tell me about your self", 
        "education and career experience",
        "can u design a photo"
    ]
}'

echo "Test payload: $test_payload"
direct_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    $TRANSFORMER_URL)
direct_http_code=$(echo "$direct_response" | tail -n1)
direct_body=$(echo "$direct_response" | head -n -1)

if [[ "$direct_http_code" == "200" ]] || [[ "$direct_http_code" == "404" ]]; then
    echo -e "${GREEN}✅ Direct transformer model status: $direct_http_code${NC}"
    echo "Response: $direct_body" | jq . 2>/dev/null || echo "Response: $direct_body"
else
    echo -e "${RED}❌ Direct transformer model status: $direct_http_code${NC}"
    echo "Response: $direct_body"
fi
echo ""

# Summary
echo -e "${BLUE}📊 AI Integration Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Local API: $API_BASE"
echo "Transformer Model: $TRANSFORMER_URL"
echo "Timestamp: $(date)"
echo ""
echo -e "${GREEN}✅ AI transformer model integration testing completed${NC}"
echo ""
echo -e "${BLUE}💡 Key Features:${NC}"
echo "  ✅ AI-powered question matching using transformer model"
echo "  ✅ Confidence threshold filtering for better accuracy"
echo "  ✅ Fallback to 'no match' when confidence is too low"
echo "  ✅ Dataset automatically extracted from knowledge base"
echo "  ✅ Real-time AI model integration with external service"
echo ""
echo -e "${BLUE}🎯 Usage Examples:${NC}"
echo ""
echo "# Health check with AI model status"
echo "curl $API_BASE/health"
echo ""
echo "# Test transformer model directly"
echo "curl $API_BASE/test-transformer"
echo ""
echo "# Query with AI matching"
echo "curl -X POST -H 'Content-Type: application/json' \\"
echo "  -d '{\"question\": \"what can you do with kotlin\"}' \\"
echo "  $API_BASE/query" 