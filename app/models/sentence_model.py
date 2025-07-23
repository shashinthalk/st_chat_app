"""
Sentence Transformer Model Service

This module handles the sentence transformer model loading, embedding operations,
and model context management within the Flask application.
"""

import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from flask import current_app, g

logger = logging.getLogger(__name__)


def init_sentence_model(app):
    """
    Initialize the sentence transformer model and store in app context.
    
    Args:
        app: Flask application instance
    """
    try:
        model_name = app.config['MODEL_NAME']
        app.logger.info(f"Loading sentence transformer model: {model_name}")
        
        # Load the model and store in app config
        model = SentenceTransformer(model_name)
        app.config['SENTENCE_MODEL'] = model
        
        app.logger.info("Sentence transformer model loaded successfully")
        
    except Exception as e:
        app.logger.error(f"Failed to load sentence transformer model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")


def get_sentence_model() -> SentenceTransformer:
    """
    Get the sentence transformer model from Flask application context.
    
    Returns:
        SentenceTransformer: The loaded sentence transformer model
        
    Raises:
        RuntimeError: If model is not loaded
    """
    model = current_app.config.get('SENTENCE_MODEL')
    if model is None:
        raise RuntimeError("Sentence transformer model not loaded")
    return model


class EmbeddingService:
    """Service class for handling sentence embedding operations."""
    
    @staticmethod
    def embed_text(text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            np.ndarray: Text embedding vector
            
        Raises:
            RuntimeError: If model is not available or embedding fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            model = get_sentence_model()
            embedding = model.encode([text.strip()])  # Returns array of shape (1, embedding_dim)
            return embedding[0]  # Return single embedding vector
            
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise RuntimeError(f"Text embedding failed: {e}")
    
    @staticmethod
    def embed_texts(texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple text strings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            np.ndarray: Array of embedding vectors with shape (n_texts, embedding_dim)
            
        Raises:
            RuntimeError: If model is not available or embedding fails
        """
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        # Filter out empty texts and strip whitespace
        clean_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not clean_texts:
            raise ValueError("No valid texts found after filtering")
        
        try:
            model = get_sentence_model()
            embeddings = model.encode(clean_texts)
            logger.info(f"Generated embeddings for {len(clean_texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            raise RuntimeError(f"Batch text embedding failed: {e}")
    
    @staticmethod
    def embed_questions_from_documents(documents: List[dict]) -> tuple[np.ndarray, List[dict]]:
        """
        Extract questions from documents and generate embeddings.
        
        Args:
            documents: List of document dictionaries with 'question' field
            
        Returns:
            tuple: (embeddings array, processed documents list)
            
        Raises:
            RuntimeError: If embedding process fails
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        try:
            questions = []
            valid_documents = []
            
            for doc in documents:
                if 'question' not in doc:
                    logger.warning(f"Document missing 'question' field: {doc.get('_id', 'unknown')}")
                    continue
                
                question = doc['question']
                if question and question.strip():
                    questions.append(question.strip())
                    valid_documents.append(doc)
                else:
                    logger.warning(f"Empty question in document: {doc.get('_id', 'unknown')}")
            
            if not questions:
                raise ValueError("No valid questions found in documents")
            
            embeddings = EmbeddingService.embed_texts(questions)
            
            logger.info(f"Successfully embedded {len(questions)} questions from documents")
            return embeddings, valid_documents
            
        except Exception as e:
            logger.error(f"Failed to embed questions from documents: {e}")
            raise RuntimeError(f"Document question embedding failed: {e}")


class ModelHealthChecker:
    """Service for checking model health and status."""
    
    @staticmethod
    def is_model_loaded() -> bool:
        """
        Check if the sentence transformer model is loaded and available.
        
        Returns:
            bool: True if model is loaded, False otherwise
        """
        try:
            model = current_app.config.get('SENTENCE_MODEL')
            return model is not None
        except:
            return False
    
    @staticmethod
    def get_model_info() -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            dict: Model information including name, status, and capabilities
        """
        try:
            if not ModelHealthChecker.is_model_loaded():
                return {
                    'status': 'not_loaded',
                    'model_name': current_app.config.get('MODEL_NAME', 'unknown'),
                    'loaded': False
                }
            
            model = get_sentence_model()
            model_name = current_app.config.get('MODEL_NAME', 'unknown')
            
            # Try a test embedding to verify model works
            try:
                test_embedding = model.encode(["test"])
                embedding_dim = test_embedding.shape[1] if len(test_embedding.shape) > 1 else len(test_embedding[0])
                
                return {
                    'status': 'healthy',
                    'model_name': model_name,
                    'loaded': True,
                    'embedding_dimension': embedding_dim,
                    'test_successful': True
                }
            except Exception as e:
                logger.warning(f"Model loaded but test embedding failed: {e}")
                return {
                    'status': 'loaded_but_unhealthy',
                    'model_name': model_name,
                    'loaded': True,
                    'test_successful': False,
                    'error': str(e)
                }
                
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                'status': 'error',
                'loaded': False,
                'error': str(e)
            } 