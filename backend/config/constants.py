"""
Configuration constants for VieMedChat backend
Centralized location for all magic numbers and configuration values
"""


# ==========================================
# RAG Configuration
# ==========================================
class RAGConfig:
    """Configuration for RAG (Retrieval-Augmented Generation) pipeline"""

    # Search settings
    TOP_K = 5  # Number of documents to retrieve
    VECTOR_SEARCH_K = 5  # K for vector search
    BM25_SEARCH_K = 5  # K for BM25 search

    # Weights for hybrid search
    VECTOR_WEIGHT = 0.6
    BM25_WEIGHT = 0.4

    # Reranker settings
    RERANK_THRESHOLD = 0.3  # Minimum score to keep document after reranking
    RERANK_TOP_N = 5  # Number of top documents after reranking

    # Model names
    DEFAULT_EMBEDDING_MODEL = "BAAI/bge-m3"
    DEFAULT_RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
    DEFAULT_LLM_MODEL = "models/gemini-2.0-flash"


# ==========================================
# Chat Configuration
# ==========================================
class ChatConfig:
    """Configuration for chat functionality"""

    # History limits
    CHAT_HISTORY_LIMIT = 10  # Maximum messages to include in context

    # LLM settings
    DEFAULT_TEMPERATURE = 0.4
    CHAT_TEMPERATURE = 0.7  # Higher for more natural conversation
    MAX_OUTPUT_TOKENS = 4096


# ==========================================
# Database Configuration
# ==========================================
class DBConfig:
    """Configuration for database"""

    # Connection pool
    MIN_CONNECTIONS = 1
    MAX_CONNECTIONS = 20


# ==========================================
# JWT Configuration
# ==========================================
class JWTConfig:
    """Configuration for JWT authentication"""

    TOKEN_EXPIRY_DAYS = 7


# ==========================================
# API Configuration
# ==========================================
class APIConfig:
    """Configuration for API settings"""

    # Rate limiting (if implemented)
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000
