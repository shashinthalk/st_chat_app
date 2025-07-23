"""
Similarity Calculation Utilities

This module provides utilities for calculating similarity between embeddings
and finding the best matches based on configurable thresholds.
"""

import logging
from typing import Tuple, Optional, List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import current_app

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Utility class for similarity calculations and matching."""
    
    @staticmethod
    def calculate_cosine_similarity(query_embedding: np.ndarray, 
                                  document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Single query embedding vector
            document_embeddings: Array of document embeddings
            
        Returns:
            np.ndarray: Array of similarity scores
            
        Raises:
            ValueError: If embeddings have incompatible shapes
        """
        try:
            # Ensure query_embedding is 2D for sklearn
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_embedding, document_embeddings)[0]
            
            logger.debug(f"Calculated similarities for {len(similarities)} documents")
            return similarities
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            raise ValueError(f"Similarity calculation failed: {e}")
    
    @staticmethod
    def find_best_match(query_embedding: np.ndarray,
                       document_embeddings: np.ndarray,
                       documents: List[Dict[str, Any]],
                       threshold: Optional[float] = None) -> Tuple[Optional[Dict], float, int]:
        """
        Find the best matching document based on similarity threshold.
        
        Args:
            query_embedding: Single query embedding vector
            document_embeddings: Array of document embeddings
            documents: List of documents corresponding to embeddings
            threshold: Minimum similarity threshold (uses config if None)
            
        Returns:
            Tuple: (best_document or None, best_similarity_score, best_index or -1)
            
        Raises:
            ValueError: If inputs are invalid or incompatible
        """
        if len(documents) != len(document_embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        if len(documents) == 0:
            logger.warning("No documents provided for matching")
            return None, 0.0, -1
        
        try:
            # Use threshold from config if not provided
            if threshold is None:
                threshold = current_app.config.get('SIMILARITY_THRESHOLD', 0.6)
            
            # Calculate similarities
            similarities = SimilarityCalculator.calculate_cosine_similarity(
                query_embedding, document_embeddings
            )
            
            # Find the best match
            best_index = int(np.argmax(similarities))
            best_similarity = float(similarities[best_index])
            
            logger.info(f"Best match similarity: {best_similarity:.4f}, threshold: {threshold}")
            
            # Check if best match meets threshold
            if best_similarity >= threshold:
                best_document = documents[best_index]
                logger.info(f"Found matching document with similarity {best_similarity:.4f}")
                return best_document, best_similarity, int(best_index)
            else:
                logger.info(f"No match found above threshold {threshold} (best: {best_similarity:.4f})")
                return None, best_similarity, int(best_index)
                
        except Exception as e:
            logger.error(f"Failed to find best match: {e}")
            raise ValueError(f"Best match calculation failed: {e}")
    
    @staticmethod
    def get_top_matches(query_embedding: np.ndarray,
                       document_embeddings: np.ndarray,
                       documents: List[Dict[str, Any]],
                       top_k: int = 5,
                       threshold: Optional[float] = None) -> List[Tuple[Dict, float, int]]:
        """
        Get top K matching documents above threshold.
        
        Args:
            query_embedding: Single query embedding vector
            document_embeddings: Array of document embeddings
            documents: List of documents corresponding to embeddings
            top_k: Number of top matches to return
            threshold: Minimum similarity threshold (uses config if None)
            
        Returns:
            List[Tuple]: List of (document, similarity_score, index) for top matches
            
        Raises:
            ValueError: If inputs are invalid or incompatible
        """
        if len(documents) != len(document_embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        if len(documents) == 0:
            return []
        
        try:
            # Use threshold from config if not provided
            if threshold is None:
                threshold = current_app.config.get('SIMILARITY_THRESHOLD', 0.6)
            
            # Calculate similarities
            similarities = SimilarityCalculator.calculate_cosine_similarity(
                query_embedding, document_embeddings
            )
            
            # Get indices sorted by similarity (descending)
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Filter by threshold and get top_k
            top_matches = []
            for idx in sorted_indices[:top_k]:
                idx = int(idx)  # Convert numpy int64 to Python int
                similarity = float(similarities[idx])
                if similarity >= threshold:
                    top_matches.append((documents[idx], similarity, idx))
                else:
                    break  # Since sorted, no more matches will meet threshold
            
            logger.info(f"Found {len(top_matches)} matches above threshold {threshold}")
            return top_matches
            
        except Exception as e:
            logger.error(f"Failed to get top matches: {e}")
            raise ValueError(f"Top matches calculation failed: {e}")


class ThresholdValidator:
    """Utility class for validating and managing similarity thresholds."""
    
    @staticmethod
    def validate_threshold(threshold: float) -> bool:
        """
        Validate that threshold is within acceptable range.
        
        Args:
            threshold: Threshold value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(threshold, (int, float)) and 0.0 <= threshold <= 1.0
    
    @staticmethod
    def get_effective_threshold(provided_threshold: Optional[float] = None) -> float:
        """
        Get the effective threshold to use, with fallback to config.
        
        Args:
            provided_threshold: Threshold provided in request (optional)
            
        Returns:
            float: Effective threshold to use
            
        Raises:
            ValueError: If threshold is invalid
        """
        if provided_threshold is not None:
            if not ThresholdValidator.validate_threshold(provided_threshold):
                raise ValueError(f"Invalid threshold: {provided_threshold}. Must be between 0.0 and 1.0")
            return float(provided_threshold)
        
        # Use config threshold
        config_threshold = current_app.config.get('SIMILARITY_THRESHOLD', 0.6)
        if not ThresholdValidator.validate_threshold(config_threshold):
            logger.warning(f"Invalid config threshold {config_threshold}, using default 0.6")
            return 0.6
        
        return float(config_threshold)


class SimilarityMetrics:
    """Utility class for calculating various similarity metrics and statistics."""
    
    @staticmethod
    def get_similarity_statistics(similarities: np.ndarray) -> Dict[str, float]:
        """
        Calculate statistical metrics for similarity scores.
        
        Args:
            similarities: Array of similarity scores
            
        Returns:
            dict: Statistical metrics including min, max, mean, std
        """
        if len(similarities) == 0:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'std': 0.0,
                'count': 0
            }
        
        return {
            'min': float(np.min(similarities)),
            'max': float(np.max(similarities)),
            'mean': float(np.mean(similarities)),
            'std': float(np.std(similarities)),
            'count': len(similarities)
        }
    
    @staticmethod
    def calculate_confidence_score(similarity: float, 
                                 statistics: Dict[str, float],
                                 threshold: float) -> float:
        """
        Calculate a confidence score based on similarity and dataset statistics.
        
        Args:
            similarity: The similarity score
            statistics: Similarity statistics from the dataset
            threshold: The threshold used
            
        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if statistics['count'] == 0 or statistics['max'] == statistics['min']:
            return 0.0
        
        # Normalize similarity relative to dataset range
        normalized = (similarity - statistics['min']) / (statistics['max'] - statistics['min'])
        
        # Factor in how much above threshold the similarity is
        threshold_factor = max(0, (similarity - threshold) / (1.0 - threshold))
        
        # Combine factors for final confidence
        confidence = (normalized * 0.7) + (threshold_factor * 0.3)
        
        return min(1.0, max(0.0, confidence)) 