"""
API Routes

This module defines the Flask API endpoints including health check and query endpoints
with proper request validation, error handling, and response formatting.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from app.database.mongodb import DocumentService
from app.models.sentence_model import EmbeddingService, ModelHealthChecker
from app.utils.similarity import SimilarityCalculator, ThresholdValidator

logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint that provides comprehensive system status.
    
    Returns:
        JSON response with health status, model status, and database connectivity
    """
    try:
        # Check model health
        model_info = ModelHealthChecker.get_model_info()
        
        # Check database connectivity
        try:
            # Try to get document count to verify DB connection
            documents = DocumentService.get_all_documents()
            db_status = {
                'status': 'healthy',
                'connected': True,
                'document_count': len(documents)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e)
            }
        
        # Determine overall health
        overall_healthy = (
            model_info.get('status') == 'healthy' and 
            db_status.get('status') == 'healthy'
        )
        
        response = {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'timestamp': None,  # Will be added by Flask if needed
            'model': model_info,
            'database': db_status,
            'config': {
                'similarity_threshold': current_app.config.get('SIMILARITY_THRESHOLD', 0.6),
                'mongodb_database': current_app.config.get('MONGODB_DATABASE'),
                'mongodb_collection': current_app.config.get('MONGODB_COLLECTION')
            }
        }
        
        status_code = 200 if overall_healthy else 503
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed',
            'details': str(e)
        }), 500


@api_bp.route('/query', methods=['POST'])
def query_endpoint():
    """
    Main query endpoint for semantic search against MongoDB documents.
    
    Expected JSON payload:
    {
        "question": "user question here",
        "threshold": 0.7  // optional, overrides config
    }
    
    Returns:
        JSON response with matched answer or 404 if no match found
    """
    try:
        # Validate request content type
        if not request.is_json:
            logger.warning("Query request without JSON content type")
            return jsonify({
                'error': 'Request must have Content-Type: application/json',
                'status_code': 400
            }), 400
        
        # Get and validate JSON data
        try:
            data = request.get_json()
        except BadRequest as e:
            logger.warning(f"Invalid JSON in query request: {e}")
            return jsonify({
                'error': 'Invalid JSON format in request body',
                'status_code': 400
            }), 400
        
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
        
        # Validate optional threshold
        custom_threshold = None
        if 'threshold' in data:
            try:
                custom_threshold = ThresholdValidator.get_effective_threshold(data['threshold'])
            except ValueError as e:
                return jsonify({
                    'error': f'Invalid threshold: {str(e)}',
                    'status_code': 400
                }), 400
        
        # Log the incoming query
        logger.info(f"Processing query: '{question[:100]}...' with threshold: {custom_threshold}")
        
        # Get documents from MongoDB
        try:
            documents = DocumentService.get_questions_for_embedding()
            if not documents:
                logger.warning("No documents found in database")
                return jsonify({
                    'error': 'No data available for search',
                    'status_code': 503
                }), 503
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return jsonify({
                'error': 'Database error occurred',
                'status_code': 500
            }), 500
        
        # Generate embeddings for documents and query
        try:
            # Embed all questions from documents
            document_embeddings, valid_documents = EmbeddingService.embed_questions_from_documents(documents)
            
            # Embed the user query
            query_embedding = EmbeddingService.embed_text(question.strip())
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return jsonify({
                'error': 'Failed to process query - embedding error',
                'status_code': 500
            }), 500
        
        # Find best match using similarity calculation
        try:
            best_document, similarity_score, best_index = SimilarityCalculator.find_best_match(
                query_embedding=query_embedding,
                document_embeddings=document_embeddings,
                documents=valid_documents,
                threshold=custom_threshold
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return jsonify({
                'error': 'Failed to process query - similarity calculation error',
                'status_code': 500
            }), 500
        
        # Handle no match found (below threshold)
        if best_document is None:
            effective_threshold = custom_threshold or current_app.config.get('SIMILARITY_THRESHOLD', 0.6)
            logger.info(f"No match found above threshold {effective_threshold} (best similarity: {similarity_score:.4f})")
            
            return jsonify({
                'error': 'No matching data found.',
                'details': {
                    'best_similarity': round(similarity_score, 4),
                    'threshold_used': effective_threshold,
                    'total_documents_searched': len(valid_documents)
                },
                'status_code': 404
            }), 404
        
        # Prepare successful response
        response = {
            'matched_question': best_document['question'],
            'answers': best_document['answers'],
            'similarity_score': round(similarity_score, 4),
            'metadata': {
                'document_id': best_document.get('_id'),
                'threshold_used': custom_threshold or current_app.config.get('SIMILARITY_THRESHOLD', 0.6),
                'total_documents_searched': len(valid_documents),
                'match_index': best_index
            }
        }
        
        logger.info(f"Successfully matched query with similarity {similarity_score:.4f}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred while processing your query',
            'status_code': 500
        }), 500


@api_bp.route('/query/batch', methods=['POST'])
def batch_query_endpoint():
    """
    Batch query endpoint for processing multiple questions at once.
    
    Expected JSON payload:
    {
        "questions": ["question1", "question2", ...],
        "threshold": 0.7,  // optional
        "top_k": 3  // optional, number of results per question
    }
    
    Returns:
        JSON response with results for each question
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Request must have Content-Type: application/json',
                'status_code': 400
            }), 400
        
        data = request.get_json()
        if not data or 'questions' not in data:
            return jsonify({
                'error': 'Missing required field: questions',
                'status_code': 400
            }), 400
        
        questions = data['questions']
        if not isinstance(questions, list) or not questions:
            return jsonify({
                'error': 'Field "questions" must be a non-empty list',
                'status_code': 400
            }), 400
        
        # Validate questions
        for i, q in enumerate(questions):
            if not isinstance(q, str) or not q.strip():
                return jsonify({
                    'error': f'Question at index {i} must be a non-empty string',
                    'status_code': 400
                }), 400
        
        # Get optional parameters
        custom_threshold = None
        if 'threshold' in data:
            try:
                custom_threshold = ThresholdValidator.get_effective_threshold(data['threshold'])
            except ValueError as e:
                return jsonify({
                    'error': f'Invalid threshold: {str(e)}',
                    'status_code': 400
                }), 400
        
        top_k = data.get('top_k', 1)
        if not isinstance(top_k, int) or top_k < 1 or top_k > 10:
            return jsonify({
                'error': 'Field "top_k" must be an integer between 1 and 10',
                'status_code': 400
            }), 400
        
        logger.info(f"Processing batch query with {len(questions)} questions")
        
        # Get documents
        documents = DocumentService.get_questions_for_embedding()
        if not documents:
            return jsonify({
                'error': 'No data available for search',
                'status_code': 503
            }), 503
        
        # Generate embeddings for documents
        document_embeddings, valid_documents = EmbeddingService.embed_questions_from_documents(documents)
        
        # Process each question
        results = []
        for i, question in enumerate(questions):
            try:
                query_embedding = EmbeddingService.embed_text(question.strip())
                
                if top_k == 1:
                    best_document, similarity_score, best_index = SimilarityCalculator.find_best_match(
                        query_embedding, document_embeddings, valid_documents, custom_threshold
                    )
                    
                    if best_document:
                        results.append({
                            'question_index': i,
                            'query': question,
                            'matches': [{
                                'matched_question': best_document['question'],
                                'answers': best_document['answers'],
                                'similarity_score': round(similarity_score, 4),
                                'document_id': best_document.get('_id')
                            }]
                        })
                    else:
                        results.append({
                            'question_index': i,
                            'query': question,
                            'matches': [],
                            'no_match_reason': f'No match above threshold {custom_threshold or current_app.config.get("SIMILARITY_THRESHOLD", 0.6)}'
                        })
                else:
                    top_matches = SimilarityCalculator.get_top_matches(
                        query_embedding, document_embeddings, valid_documents, top_k, custom_threshold
                    )
                    
                    matches = []
                    for doc, score, idx in top_matches:
                        matches.append({
                            'matched_question': doc['question'],
                            'answers': doc['answers'],
                            'similarity_score': round(score, 4),
                            'document_id': doc.get('_id')
                        })
                    
                    results.append({
                        'question_index': i,
                        'query': question,
                        'matches': matches
                    })
                    
            except Exception as e:
                logger.error(f"Failed to process question {i}: {e}")
                results.append({
                    'question_index': i,
                    'query': question,
                    'error': 'Failed to process this question',
                    'matches': []
                })
        
        return jsonify({
            'results': results,
            'metadata': {
                'total_questions': len(questions),
                'total_documents_searched': len(valid_documents),
                'threshold_used': custom_threshold or current_app.config.get('SIMILARITY_THRESHOLD', 0.6),
                'top_k': top_k
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in batch query endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred while processing batch query',
            'status_code': 500
        }), 500


# Error handlers specific to API blueprint
@api_bp.errorhandler(400)
def api_bad_request(error):
    """Handle 400 errors within API blueprint."""
    return jsonify({
        'error': 'Bad Request',
        'message': 'The request could not be understood or was missing required parameters.',
        'status_code': 400
    }), 400


@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors within API blueprint."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist.',
        'available_endpoints': ['/health', '/query', '/query/batch'],
        'status_code': 404
    }), 404 