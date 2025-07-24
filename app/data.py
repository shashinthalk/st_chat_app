"""
Simple Q&A data for the Flask API
"""

# Legacy fallback data - now using external API
# This data is kept as a fallback in case the external API is unavailable

FALLBACK_QA_DATA = [
    {
        "question": "What is machine learning?",
        "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task."
    },
    {
        "question": "What is artificial intelligence?",
        "answer": "Artificial Intelligence (AI) is a branch of computer science that aims to create machines and systems that can perform tasks that typically require human intelligence, such as learning, reasoning, problem-solving, and understanding natural language."
    }
]

# Note: The application now uses external API from https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data
# This fallback data is only used if the external API is unavailable 