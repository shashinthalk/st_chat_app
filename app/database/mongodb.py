"""
MongoDB Database Access Layer

This module handles all MongoDB operations including connection management,
document retrieval, and database initialization.
"""

import logging
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from flask import current_app, g

logger = logging.getLogger(__name__)


def init_db(app):
    """
    Initialize MongoDB connection and store client in app context.
    
    Args:
        app: Flask application instance
    """
    try:
        app.config['MONGO_CLIENT'] = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test the connection
        app.config['MONGO_CLIENT'].admin.command('ismaster')
        app.logger.info(f"Connected to MongoDB: {app.config['MONGODB_URI']}")
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        app.logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError(f"MongoDB connection failed: {e}")


def get_db():
    """
    Get database connection from Flask application context.
    
    Returns:
        Database: MongoDB database instance
    """
    if 'db' not in g:
        mongo_client = current_app.config['MONGO_CLIENT']
        g.db = mongo_client[current_app.config['MONGODB_DATABASE']]
    return g.db


def get_collection():
    """
    Get the Q&A documents collection.
    
    Returns:
        Collection: MongoDB collection instance for Q&A documents
    """
    db = get_db()
    return db[current_app.config['MONGODB_COLLECTION']]


class DocumentService:
    """Service class for handling Q&A document operations."""
    
    @staticmethod
    def get_all_documents() -> List[Dict[str, Any]]:
        """
        Retrieve all Q&A documents from MongoDB.
        
        Returns:
            List[Dict]: List of all Q&A documents
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            collection = get_collection()
            documents = list(collection.find({}))
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            logger.info(f"Retrieved {len(documents)} documents from MongoDB")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents from MongoDB: {e}")
            raise RuntimeError(f"Database operation failed: {e}")
    
    @staticmethod
    def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.
        
        Args:
            doc_id: Document ID to retrieve
            
        Returns:
            Dict or None: Document if found, None otherwise
        """
        try:
            from bson import ObjectId
            collection = get_collection()
            
            # Try to convert to ObjectId if it's a valid ObjectId string
            try:
                query = {'_id': ObjectId(doc_id)}
            except:
                # If not a valid ObjectId, search by string ID
                query = {'_id': doc_id}
            
            document = collection.find_one(query)
            
            if document and '_id' in document:
                document['_id'] = str(document['_id'])
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to retrieve document {doc_id}: {e}")
            return None
    
    @staticmethod
    def validate_document_structure(document: Dict[str, Any]) -> bool:
        """
        Validate that a document has the expected structure.
        
        Args:
            document: Document to validate
            
        Returns:
            bool: True if valid structure, False otherwise
        """
        required_fields = ['question', 'answers']
        
        if not all(field in document for field in required_fields):
            return False
        
        # Validate answers structure
        answers = document.get('answers', {})
        if not isinstance(answers, dict):
            return False
        
        # Optional: Validate specific answer fields
        expected_answer_fields = ['title', 'subtitle', 'about', 'projects', 'whyWorkWithMe', 'callToAction']
        # Note: We don't require all fields to be present, just that answers is a dict
        
        return True
    
    @staticmethod
    def get_questions_for_embedding() -> List[Dict[str, Any]]:
        """
        Get all documents and extract questions for embedding.
        
        Returns:
            List[Dict]: List of documents with question and ID for embedding
        """
        try:
            documents = DocumentService.get_all_documents()
            valid_documents = []
            
            for doc in documents:
                if DocumentService.validate_document_structure(doc):
                    valid_documents.append({
                        '_id': doc['_id'],
                        'question': doc['question'],
                        'answers': doc['answers']
                    })
                else:
                    logger.warning(f"Invalid document structure for document {doc.get('_id', 'unknown')}")
            
            logger.info(f"Found {len(valid_documents)} valid documents for embedding")
            return valid_documents
            
        except Exception as e:
            logger.error(f"Failed to get questions for embedding: {e}")
            raise RuntimeError(f"Failed to prepare questions for embedding: {e}")


def close_db(error=None):
    """
    Close database connection.
    
    Args:
        error: Any error that occurred (optional)
    """
    db = g.pop('db', None)
    if db is not None:
        # Connection is automatically handled by pymongo
        pass


def init_app_db_handlers(app):
    """
    Initialize database-related app handlers.
    
    Args:
        app: Flask application instance
    """
    app.teardown_appcontext(close_db) 