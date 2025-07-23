"""
Production-Optimized Sentence Transformer Model Service

This module provides the most optimized sentence transformer implementation
for production deployment with memory monitoring and aggressive cleanup.
"""

import logging
import gc
import os
import psutil
import threading
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from flask import current_app, g
import torch

logger = logging.getLogger(__name__)

# Global model instance and lock for thread safety
_model_instance = None
_model_lock = threading.Lock()


def log_memory_usage(context: str):
    """Log current memory usage for monitoring."""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger.info(f"Memory usage {context}: {memory_mb:.1f} MB (RSS), {memory_info.vms / 1024 / 1024:.1f} MB (VMS)")
        
        # Log system memory if available
        try:
            sys_memory = psutil.virtual_memory()
            logger.info(f"System memory {context}: {sys_memory.percent}% used, {sys_memory.available / 1024 / 1024:.1f} MB available")
        except:
            pass
    except Exception as e:
        logger.warning(f"Could not log memory usage: {e}")


def init_sentence_model_optimized(app):
    """
    Initialize production-optimized sentence transformer model.
    
    Args:
        app: Flask application instance
    """
    global _model_instance
    
    with _model_lock:
        if _model_instance is not None:
            app.logger.info("Model already loaded, reusing instance")
            app.config['SENTENCE_MODEL'] = _model_instance
            return
    
    try:
        model_name = app.config['MODEL_NAME']
        app.logger.info(f"Loading OPTIMIZED sentence transformer model: {model_name}")
        
        log_memory_usage("before model loading")
        
        # Set critical environment variables to prevent multiple format downloads
        os.environ.update({
            'SENTENCE_TRANSFORMERS_HOME': '/tmp/sentence_transformers',
            'HF_HOME': '/tmp/huggingface',
            'TRANSFORMERS_CACHE': '/tmp/transformers_cache',
            'SENTENCE_TRANSFORMERS_DISABLE_ONNX': '1',
            'SENTENCE_TRANSFORMERS_DISABLE_OPENVINO': '1',
            'PYTORCH_TRANSFORMERS_CACHE': '/tmp/transformers_cache',
            'HF_DATASETS_OFFLINE': '1',
        })
        
        # Load model with most optimized settings
        model = SentenceTransformer(
            model_name,
            device='cpu',
            cache_folder='/tmp/sentence_transformers',
            use_auth_token=False
        )
        
        # Aggressive optimization for inference
        model.eval()
        for param in model.parameters():
            param.requires_grad = False
        
        # Enable optimizations
        if hasattr(torch, 'set_num_threads'):
            torch.set_num_threads(2)  # Limit threads for memory efficiency
        
        # Store in global and app config
        with _model_lock:
            _model_instance = model
        app.config['SENTENCE_MODEL'] = model
        
        # Force cleanup after loading
        gc.collect()
        
        log_memory_usage("after model loading")
        app.logger.info("Optimized sentence transformer model loaded successfully")
        
    except Exception as e:
        app.logger.error(f"Failed to load optimized sentence transformer model: {e}")
        raise RuntimeError(f"Optimized model loading failed: {e}")


def get_sentence_model_optimized() -> SentenceTransformer:
    """Get the optimized sentence transformer model with safety checks."""
    global _model_instance
    
    # Try from app config first
    if hasattr(current_app, 'config'):
        model = current_app.config.get('SENTENCE_MODEL')
        if model is not None:
            return model
    
    # Fallback to global instance
    with _model_lock:
        if _model_instance is not None:
            return _model_instance
    
    raise RuntimeError("Optimized sentence transformer model not loaded")


class OptimizedEmbeddingService:
    """Production-optimized embedding service with aggressive memory management."""
    
    @staticmethod
    def embed_text_optimized(text: str) -> np.ndarray:
        """Generate embedding with maximum optimization."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            model = get_sentence_model_optimized()
            
            with torch.no_grad():
                # Single text embedding with all optimizations
                embedding = model.encode(
                    [text.strip()], 
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True,
                    batch_size=1,  # Force single item processing
                    device='cpu'
                )
            
            # Immediate cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            return embedding[0].astype(np.float32)  # Use float32 for memory efficiency
            
        except Exception as e:
            logger.error(f"Failed to embed text optimally: {e}")
            raise RuntimeError(f"Optimized text embedding failed: {e}")
    
    @staticmethod
    def embed_texts_optimized(texts: List[str]) -> np.ndarray:
        """Generate embeddings with maximum memory efficiency and batch processing."""
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        clean_texts = [text.strip() for text in texts if text and text.strip()]
        if not clean_texts:
            raise ValueError("No valid texts found after filtering")
        
        try:
            model = get_sentence_model_optimized()
            
            # Ultra-small batches for memory efficiency
            batch_size = 4  # Very conservative for 8GB server
            embeddings = []
            
            log_memory_usage(f"before batch embedding {len(clean_texts)} texts")
            
            with torch.no_grad():
                for i in range(0, len(clean_texts), batch_size):
                    batch = clean_texts[i:i + batch_size]
                    
                    batch_embeddings = model.encode(
                        batch, 
                        show_progress_bar=False,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        batch_size=len(batch),
                        device='cpu'
                    )
                    
                    # Convert to float32 for memory efficiency
                    batch_embeddings = batch_embeddings.astype(np.float32)
                    embeddings.append(batch_embeddings)
                    
                    # Aggressive cleanup after each batch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    gc.collect()
                    
                    logger.debug(f"Processed batch {i//batch_size + 1}/{(len(clean_texts) + batch_size - 1)//batch_size}")
            
            # Concatenate results efficiently
            all_embeddings = np.vstack(embeddings) if len(embeddings) > 1 else embeddings[0]
            
            log_memory_usage(f"after batch embedding {len(clean_texts)} texts")
            logger.info(f"Generated optimized embeddings for {len(clean_texts)} texts")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to embed texts optimally: {e}")
            raise RuntimeError(f"Optimized batch embedding failed: {e}")
    
    @staticmethod
    def cleanup_memory():
        """Force memory cleanup - call after processing requests."""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            logger.debug("Memory cleanup completed")
        except Exception as e:
            logger.warning(f"Memory cleanup failed: {e}")


# Memory monitoring decorator
def monitor_memory(func):
    """Decorator to monitor memory usage around function calls."""
    def wrapper(*args, **kwargs):
        log_memory_usage(f"before {func.__name__}")
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            log_memory_usage(f"after {func.__name__}")
            OptimizedEmbeddingService.cleanup_memory()
    return wrapper 