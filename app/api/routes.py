"""
Simple API Routes for Flask Q&A Service
"""

from flask import Blueprint, request, jsonify
from app.services.knowledge_base import knowledge_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with knowledge base status"""
    try:
        # Get cache info
        cache_info = knowledge_service.get_cache_info()
        
        # Try to fetch a small sample to test API connectivity
        knowledge_data = knowledge_service.fetch_knowledge_base()
        data_count = len(knowledge_data) if knowledge_data else 0
        
        # Determine API status
        if cache_info.get('cache_status') == 'success':
            api_status = "connected"
        elif cache_info.get('cache_status') in ['fallback', 'mock']:
            api_status = "fallback_mode"
        else:
            api_status = "disconnected"
        
        return jsonify({
            'status': 'healthy',
            'message': 'Flask Q&A API is running',
            'available_endpoints': ['/health', '/query', '/cache/info', '/cache/clear', '/test-api'],
            'knowledge_base': {
                'status': api_status,
                'data_count': data_count,
                'cache_info': cache_info
            },
            'api_url': 'External Knowledge Base API (with fallback)'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'healthy',
            'message': 'Flask Q&A API is running',
            'available_endpoints': ['/health', '/query', '/cache/info', '/cache/clear', '/test-api'],
            'knowledge_base': {
                'status': 'error',
                'error': str(e)
            }
        }), 200

@api_bp.route('/query', methods=['POST'])
def query_endpoint():
    """Query endpoint using external knowledge base API - returns answer content directly"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Request must have Content-Type: application/json',
                'status_code': 400
            }), 400
        
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required field: question',
                'status_code': 400
            }), 400
        
        question = data['question']
        if not isinstance(question, str) or not question.strip():
            return jsonify({
                'error': 'Field "question" must be a non-empty string',
                'status_code': 400
            }), 400
        
        # Search knowledge base
        logger.info(f"Processing query: {question}")
        match = knowledge_service.search_knowledge_base(question)
        
        if match:
            # Extract and return only the answer content
            answers = match.get('answers', {})
            
            # Return the answer content directly
            response_data = {
                'title': answers.get('title', ''),
                'subtitle': answers.get('subtitle', ''),
                'about': answers.get('about', ''),
                'projects': answers.get('projects', []),
                'whyWorkWithMe': answers.get('whyWorkWithMe', []),
                'callToAction': answers.get('callToAction', {})
            }
            
            logger.info(f"Found match for: {question}")
            return jsonify(response_data), 200
        
        else:
            # No match found - get available questions for suggestions
            knowledge_data = knowledge_service.fetch_knowledge_base()
            available_questions = [item.get('question', '') for item in knowledge_data if item.get('question')]
            
            response_data = {
                'error': 'No matching answer found for your question',
                'question': question,
                'matched': False,
                'available_questions': available_questions[:5],  # Limit to first 5
                'suggestions': [
                    'Try asking about Kotlin development, career experience, or personal background',
                    'Ask "can u develop kotlin api backend" or "tell me about yourself"',
                    'Check the available questions list above for inspiration'
                ],
                'total_available': len(available_questions),
                'data_source': knowledge_service.get_cache_info().get('cache_status', 'unknown')
            }
            
            logger.info(f"No match found for: {question}")
            return jsonify(response_data), 404
            
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to process your question',
            'status_code': 500
        }), 500

@api_bp.route('/cache/info', methods=['GET'])
def cache_info():
    """Get information about the knowledge base cache"""
    try:
        cache_info = knowledge_service.get_cache_info()
        return jsonify({
            'cache_status': cache_info,
            'message': 'Cache information retrieved successfully'
        }), 200
    except Exception as e:
        logger.error(f"Failed to get cache info: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve cache information',
            'status_code': 500
        }), 500

@api_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the knowledge base cache to force fresh data"""
    try:
        knowledge_service.clear_cache()
        return jsonify({
            'message': 'Cache cleared successfully',
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return jsonify({
            'error': 'Failed to clear cache',
            'status_code': 500
        }), 500

@api_bp.route('/test-api', methods=['GET'])
def test_api():
    """Test the external API connection"""
    try:
        test_result = knowledge_service.test_api_connection()
        return jsonify({
            'message': 'API connection test completed',
            'test_result': test_result,
            'api_url': knowledge_service.api_url,
            'jwt_token_length': len(knowledge_service.jwt_token)
        }), 200
    except Exception as e:
        logger.error(f"Failed to test API: {str(e)}")
        return jsonify({
            'error': 'Failed to test API connection',
            'status_code': 500
        }), 500 