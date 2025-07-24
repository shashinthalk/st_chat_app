import requests
import logging
from typing import List, Dict, Optional
import time
import os

# Configure logging
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Service to interact with the external knowledge base API and transformer model"""
    
    def __init__(self):
        self.api_url = "https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data"
        self.transformer_url = "http://95.111.228.138:5002/query"
        
        # Try to get JWT token from environment variable first, then fallback to hardcoded
        self.jwt_token = os.getenv('KNOWLEDGE_BASE_JWT_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.e30.BVcRJKdpiTfPnDItgQQn9gZONWrRyc0oLIaqjlIK9Zk')
        
        self.headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "User-Agent": "Flask-QA-API/1.0"
        }
        self.timeout = 15
        self.cache = {}
        self.cache_expiry = 300  # 5 minutes
        self.last_cache_time = 0
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        return (
            self.cache and 
            time.time() - self.last_cache_time < self.cache_expiry
        )
    
    def fetch_knowledge_base(self) -> List[Dict]:
        """
        Fetch knowledge base data from external API only
        Returns cached data if available and not expired
        Returns empty list if API fails
        """
        # Return cached data if valid
        if self._is_cache_valid():
            logger.info("Returning cached knowledge base data")
            return self.cache.get('data', [])
        
        try:
            logger.info(f"Fetching knowledge base data from {self.api_url}")
            logger.debug(f"Using JWT token (first 10 chars): {self.jwt_token[:10]}...")
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Log response details for debugging
            logger.info(f"API Response Status: {response.status_code}")
            logger.debug(f"API Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response format
                if isinstance(data, list):
                    # Cache the successful response
                    self.cache = {
                        'data': data,
                        'status': 'success',
                        'count': len(data)
                    }
                    self.last_cache_time = time.time()
                    
                    logger.info(f"Successfully fetched {len(data)} knowledge base entries")
                    return data
                else:
                    logger.error(f"Unexpected response format: {type(data)}")
                    return []
            
            elif response.status_code == 401:
                logger.error("Authentication failed - invalid JWT token")
                logger.error(f"Response: {response.text}")
                logger.info("Hint: Check if KNOWLEDGE_BASE_JWT_TOKEN environment variable is set correctly")
                return []
            
            elif response.status_code == 403:
                logger.error(f"Forbidden - JWT token issue: {response.text}")
                logger.error(f"Current token (first 10 chars): {self.jwt_token[:10]}...")
                logger.info("Hint: The JWT token may be malformed or expired. Please check the token format.")
                logger.info("You can set KNOWLEDGE_BASE_JWT_TOKEN environment variable with the correct token")
                return []
            
            elif response.status_code == 404:
                logger.error("Knowledge base API endpoint not found")
                return []
            
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out after {self.timeout} seconds")
            return []
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to knowledge base API")
            logger.error("Please check your internet connection and API URL")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return []
            
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error fetching knowledge base: {str(e)}")
            return []
    
    def test_with_token(self, test_token: str) -> Dict:
        """Test the API with a specific token (for debugging)"""
        test_headers = {
            "Authorization": f"Bearer {test_token}",
            "Content-Type": "application/json",
            "User-Agent": "Flask-QA-API/1.0"
        }
        
        try:
            response = requests.get(
                self.api_url,
                headers=test_headers,
                timeout=self.timeout
            )
            
            return {
                'token_preview': f"{test_token[:10]}...",
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_preview': response.text[:200],
                'headers': dict(response.headers),
                'data_count': len(response.json()) if response.status_code == 200 else 0
            }
            
        except Exception as e:
            return {
                'token_preview': f"{test_token[:10]}...",
                'success': False,
                'error': str(e)
            }
    
    def get_questions_dataset(self) -> List[str]:
        """Extract all questions from knowledge base to create dataset for transformer model"""
        knowledge_data = self.fetch_knowledge_base()
        
        if not knowledge_data:
            logger.warning("No knowledge base data available for dataset creation")
            return []
        
        questions = []
        for entry in knowledge_data:
            if entry.get('question'):
                questions.append(entry['question'])
        
        logger.info(f"Created dataset with {len(questions)} questions")
        return questions
    
    def query_transformer_model(self, user_question: str, dataset: List[str]) -> Optional[str]:
        """
        Query the transformer model to find the best matching question
        Returns the matched question from dataset or None if no match
        """
        if not user_question or not dataset:
            return None
        
        try:
            payload = {
                "question": user_question,
                "dataset": dataset
            }
            
            logger.info(f"Querying transformer model with question: {user_question}")
            logger.info(f"Dataset size: {len(dataset)}")
            
            response = requests.post(
                self.transformer_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            logger.info(f"Transformer model response status: {response.status_code}")
            
            # Handle both 200 and 404 responses as the model may return 404 for no match
            if response.status_code in [200, 404]:
                result = response.json()
                logger.info(f"Transformer model response: {result}")
                
                # Handle the actual response format from your transformer model
                if isinstance(result, dict):
                    confidence_score = result.get('score', 0)
                    
                    # Set a confidence threshold (adjust as needed)
                    confidence_threshold = 0.5
                    
                    # Handle two different response formats:
                    # Format 1: {"result": "Not found", "score": 0.2} - for no match
                    # Format 2: {"match": "matched question", "score": 0.7} - for match found
                    
                    matched_result = None
                    if 'match' in result:
                        # Format 2: Match found
                        matched_result = result.get('match')
                        logger.info(f"Transformer found match: {matched_result}, score: {confidence_score}")
                    elif 'result' in result:
                        # Format 1: Check if it's not "Not found"
                        result_value = result.get('result')
                        if result_value and result_value != "Not found":
                            matched_result = result_value
                        logger.info(f"Transformer result: {result_value}, score: {confidence_score}")
                    
                    # Validate the match
                    if (matched_result and 
                        confidence_score >= confidence_threshold and
                        matched_result in dataset):
                        logger.info(f"Transformer model matched: {matched_result} (score: {confidence_score})")
                        return matched_result
                    else:
                        logger.info(f"Transformer model: No confident match found (result: {matched_result}, score: {confidence_score}, threshold: {confidence_threshold})")
                        return None
                
                logger.warning(f"Transformer model returned unexpected format: {result}")
                return None
            
            else:
                logger.error(f"Transformer model request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Transformer model request timed out after {self.timeout} seconds")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to transformer model")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Transformer model request failed: {str(e)}")
            return None
            
        except ValueError as e:
            logger.error(f"Failed to parse transformer model response: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error querying transformer model: {str(e)}")
            return None
    
    def search_knowledge_base(self, question: str) -> Optional[Dict]:
        """
        Search for a matching question using the transformer model
        Returns the best match or None if no match found
        """
        if not question or not question.strip():
            return None
        
        # Get knowledge base data from external API only
        knowledge_data = self.fetch_knowledge_base()
        
        if not knowledge_data:
            logger.warning("No knowledge base data available for search")
            return None
        
        # Extract questions for dataset
        dataset = self.get_questions_dataset()
        
        if not dataset:
            logger.warning("No questions available in dataset")
            return None
        
        # Query transformer model
        matched_question = self.query_transformer_model(question.strip(), dataset)
        
        if matched_question:
            # Find the corresponding entry in knowledge base
            for entry in knowledge_data:
                if entry.get('question') == matched_question:
                    logger.info(f"Found knowledge base entry for matched question: {matched_question}")
                    return entry
            
            logger.warning(f"Matched question not found in knowledge base: {matched_question}")
            return None
        
        logger.info(f"No match found by transformer model for question: {question}")
        return None
    
    def get_cache_info(self) -> Dict:
        """Get information about the current cache status"""
        return {
            'cached': bool(self.cache),
            'cache_age_seconds': time.time() - self.last_cache_time if self.last_cache_time else 0,
            'cache_expires_in': max(0, self.cache_expiry - (time.time() - self.last_cache_time)) if self.last_cache_time else 0,
            'cached_entries': len(self.cache.get('data', [])) if self.cache else 0,
            'cache_status': self.cache.get('status', 'none') if self.cache else 'none'
        }
    
    def clear_cache(self):
        """Clear the cache to force fresh data fetch"""
        self.cache = {}
        self.last_cache_time = 0
        logger.info("Knowledge base cache cleared")
    
    def test_api_connection(self) -> Dict:
        """Test the API connection and return detailed status"""
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_text': response.text[:200],
                'headers': dict(response.headers),
                'error': None,
                'token_preview': f"{self.jwt_token[:10]}...",
                'auth_header': f"Bearer {self.jwt_token[:10]}..."
            }
            
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'response_text': None,
                'headers': {},
                'error': str(e),
                'token_preview': f"{self.jwt_token[:10]}...",
                'auth_header': f"Bearer {self.jwt_token[:10]}..."
            }
    
    def test_transformer_model(self, test_question: str = "What is machine learning?") -> Dict:
        """Test the transformer model connection"""
        try:
            dataset = self.get_questions_dataset()
            if not dataset:
                return {
                    'success': False,
                    'error': 'No dataset available for testing - external API may be unavailable',
                    'response': None
                }
            
            payload = {
                "question": test_question,
                "dataset": dataset
            }
            
            response = requests.post(
                self.transformer_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            # Consider both 200 and 404 as valid responses from the transformer model
            is_success = response.status_code in [200, 404]
            response_data = None
            
            if is_success:
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
            else:
                response_data = response.text
            
            return {
                'success': is_success,
                'status_code': response.status_code,
                'response': response_data,
                'dataset_size': len(dataset),
                'test_question': test_question,
                'dataset_preview': dataset[:3],  # Show first 3 questions for debugging
                'error': None if is_success else f"HTTP {response.status_code}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'status_code': None,
                'response': None,
                'dataset_size': 0,
                'test_question': test_question,
                'dataset_preview': [],
                'error': str(e)
            }

# Global instance
knowledge_service = KnowledgeBaseService() 