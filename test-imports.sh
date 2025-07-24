#!/bin/bash

# Test script to verify all imports and AI integration components
echo "🧪 Testing Flask Q&A API with AI Integration - Import Tests"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Testing Core Imports${NC}"
echo ""

# Test 1: Flask app creation
echo -e "${YELLOW}Test 1: Flask app creation${NC}"
if python -c "from app import create_app; app = create_app(); print('✅ Flask app created successfully')"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Test 2: Fallback Q&A data loading
echo -e "${YELLOW}Test 2: Fallback Q&A data loading${NC}"
if python -c "from app.data import FALLBACK_QA_DATA; print(f'✅ Fallback Q&A data loaded: {len(FALLBACK_QA_DATA)} items')"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Test 3: AI transformer service initialization
echo -e "${YELLOW}Test 3: AI transformer service initialization${NC}"
if python -c "from app.services.knowledge_base import knowledge_service; print(f'✅ AI transformer service initialized: {knowledge_service.transformer_url}')"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Test 4: API routes import
echo -e "${YELLOW}Test 4: API routes import${NC}"
if python -c "from app.api.routes import api_bp; print(f'✅ API blueprint imported: {api_bp.name}')"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Test 5: Knowledge service methods
echo -e "${YELLOW}Test 5: Knowledge service methods${NC}"
if python -c "
from app.services.knowledge_base import knowledge_service
dataset = knowledge_service.get_questions_dataset()
cache_info = knowledge_service.get_cache_info()
print(f'✅ Knowledge service methods working: {len(dataset)} questions, cache status: {cache_info[\"cache_status\"]}')
"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Test 6: Complete Flask app with routes
echo -e "${YELLOW}Test 6: Complete Flask app with routes${NC}"
if python -c "
from app import create_app
app = create_app()
with app.app_context():
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    print(f'✅ Flask app with routes: {routes}')
"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
    exit 1
fi
echo ""

# Summary
echo -e "${BLUE}📊 Import Test Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All imports and components working correctly${NC}"
echo ""
echo -e "${BLUE}🚀 Ready for deployment with:${NC}"
echo "  ✅ Flask app factory pattern"
echo "  ✅ AI transformer integration"
echo "  ✅ External knowledge base API"
echo "  ✅ Fallback data system"
echo "  ✅ Complete API endpoints"
echo ""
echo -e "${BLUE}🎯 Next steps:${NC}"
echo "  • Run: python run.py (local development)"
echo "  • Run: ./build-and-test.sh (Docker build & test)"
echo "  • Push to main (GitHub Actions deployment)"
echo ""
echo -e "${GREEN}🎉 Import tests completed successfully!${NC}" 