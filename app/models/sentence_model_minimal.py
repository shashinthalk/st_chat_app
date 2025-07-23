"""
Ultra-Minimal Sentence Transformer Model Service

This module provides a minimal sentence transformer implementation that only loads
the essential PyTorch model without downloading multiple formats (ONNX, OpenVINO, etc.)
"""

import logging
import gc
import os
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from flask import current_app, g
import torch

logger = logging.getLogger(__name__)


def init_sentence_model_minimal(app):
    """
    Initialize ultra-minimal sentence transformer model (PyTorch only).
    
    Args:
        app: Flask application instance
    """
    try:
        model_name = app.config['MODEL_NAME']
        app.logger.info(f"Loading MINIMAL sentence transformer model: {model_name}")
        
        # Set environment variables to minimize downloads
        os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'
        os.environ['HF_HOME'] = '/tmp/huggingface'
        os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
        
        # Disable unnecessary model formats
        os.environ['SENTENCE_TRANSFORMERS_DISABLE_ONNX'] = '1'
        os.environ['SENTENCE_TRANSFORMERS_DISABLE_OPENVINO'] = '1'
        
        # Load model with minimal settings
        model = SentenceTransformer(
            model_name, 
            device='cpu',
            cache_folder='/tmp/sentence_transformers',
            use_auth_token=False
        )
        
        # Optimize model for inference only
        model.eval()
        for param in model.parameters():
            param.requires_grad = False
            
        # Store model in app config
        app.config['SENTENCE_MODEL'] = model
        
        # Force cleanup
        gc.collect()
        
        app.logger.info("Minimal sentence transformer model loaded successfully")
        
    except Exception as e:
        app.logger.error(f"Failed to load minimal sentence transformer model: {e}")
        raise RuntimeError(f"Minimal model loading failed: {e}")


def get_sentence_model_minimal() -> SentenceTransformer:
    """Get the minimal sentence transformer model."""
    model = current_app.config.get('SENTENCE_MODEL')
    if model is None:
        raise RuntimeError("Sentence transformer model not loaded")
    return model


class MinimalEmbeddingService:
    """Ultra-minimal embedding service with aggressive optimization."""
    
    @staticmethod
    def embed_text_minimal(text: str) -> np.ndarray:
        """Generate embedding with minimal memory usage."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            model = get_sentence_model_minimal()
            
            with torch.no_grad():
                # Use convert_to_numpy=True to avoid tensor overhead
                embedding = model.encode(
                    [text.strip()], 
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
            
            # Immediate cleanup
            gc.collect()
            
            return embedding[0]
            
        except Exception as e:
            logger.error(f"Failed to embed text minimally: {e}")
            raise RuntimeError(f"Minimal text embedding failed: {e}")
    
    @staticmethod
    def embed_texts_minimal(texts: List[str]) -> np.ndarray:
        """Generate embeddings with minimal memory and batch processing."""
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        clean_texts = [text.strip() for text in texts if text and text.strip()]
        if not clean_texts:
            raise ValueError("No valid texts found after filtering")
        
        try:
            model = get_sentence_model_minimal()
            
            # Very small batches for memory efficiency
            batch_size = 8  # Even smaller than before
            embeddings = []
            
            with torch.no_grad():
                for i in range(0, len(clean_texts), batch_size):
                    batch = clean_texts[i:i + batch_size]
                    batch_embeddings = model.encode(
                        batch, 
                        show_progress_bar=False,
                        convert_to_numpy=True,
                        normalize_embeddings=True
                    )
                    embeddings.append(batch_embeddings)
                    
                    # Aggressive cleanup after each batch
                    gc.collect()
            
            # Concatenate results
            all_embeddings = np.vstack(embeddings) if len(embeddings) > 1 else embeddings[0]
            
            logger.info(f"Generated minimal embeddings for {len(clean_texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to embed texts minimally: {e}")
            raise RuntimeError(f"Minimal batch embedding failed: {e}") 