"""
Simple API Routes for Flask Q&A Service
"""

from flask import Blueprint, request, jsonify
from app.data import QA_DATA

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Flask Q&A API is running',
        'available_endpoints': ['/health', '/query'],
        'data_count': len(QA_DATA)
    }), 200


@api_bp.route('/query', methods=['POST'])
def query_endpoint():
    """
    Query endpoint for Q&A matching.
    
    Expected JSON payload:
    {
        "question": "user question here"
    }
    
    Returns:
        JSON response with matched answer or 404 if no match found
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'error': 'Request must have Content-Type: application/json',
                'status_code': 400
            }), 400
        
        # Get and validate JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body cannot be empty',
                'status_code': 400
            }), 400
        
        # Validate required fields
        if 'question' not in data:
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
        
        # Search for matching question in Q&A data
        question_lower = question.strip().lower()
        
        # Define common synonyms for better matching
        ai_keywords = ['ai', 'artificial intelligence', 'artificial', 'intelligence']
        ml_keywords = ['ml', 'machine learning', 'machine', 'learning']
        
        for qa_item in QA_DATA:
            qa_question_lower = qa_item['question'].lower()
            
            # Direct substring matching
            if question_lower in qa_question_lower or qa_question_lower in question_lower:
                return jsonify({
                    'question': qa_item['question'],
                    'answer': qa_item['answer'],
                    'matched': True,
                    'match_type': 'direct'
                }), 200
            
            # Enhanced keyword matching for AI/ML topics
            if any(keyword in question_lower for keyword in ai_keywords) and \
               any(keyword in qa_question_lower for keyword in ai_keywords):
                return jsonify({
                    'question': qa_item['question'],
                    'answer': qa_item['answer'],
                    'matched': True,
                    'match_type': 'keyword'
                }), 200
            
            if any(keyword in question_lower for keyword in ml_keywords) and \
               any(keyword in qa_question_lower for keyword in ml_keywords):
                return jsonify({
                    'question': qa_item['question'],
                    'answer': qa_item['answer'],
                    'matched': True,
                    'match_type': 'keyword'
                }), 200
        
        # No match found
        return jsonify({
            'error': 'No matching answer found for your question',
            'question': question,
            'matched': False,
            'available_questions': [item['question'] for item in QA_DATA],
            'suggestions': [
                'Try using keywords like: AI, artificial intelligence, ML, machine learning',
                'Rephrase your question to be more specific',
                'Check the available questions list above'
            ]
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': 'An error occurred while processing your request',
            'details': str(e),
            'status_code': 500
        }), 500 