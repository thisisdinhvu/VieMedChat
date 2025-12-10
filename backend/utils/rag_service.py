"""
Optimized RAG Service with caching and reduced retrieval
"""

import os
import logging
from dotenv import load_dotenv

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.routes.rag.embedding import Embedding
from backend.routes.rag.search import Searching
from backend.routes.rag.utils import load_corpus, preprocess_context
from backend.routes.rag.llms import LLM
from backend.routes.rag.reranker import Reranker

load_dotenv()
logger = logging.getLogger(__name__)


class RAGService:
    """
    Optimized RAG Pipeline with:
    - Reduced document retrieval count
    - Result caching
    - Faster reranking
    """

    def __init__(self, use_reranker=True, reranker_model="BAAI/bge-reranker-v2-m3"):
        """Initialize RAG pipeline"""
        # API Keys
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")

        # Configs
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.corpus_path = os.getenv("CORPUS_PATH")
        self.use_reranker = use_reranker
        self.reranker_model = reranker_model

        # Lazy loading attributes
        self._vectorstore = None
        self._search_engine = None
        self._splits = None
        self._llm = None
        self._reranker = None

        logger.info("RAG Service initialized (lazy loading enabled)")
        logger.info(f"   - Reranker: {'Enabled' if use_reranker else 'Disabled'}")

    @property
    def vectorstore(self):
        """Lazy load Pinecone vectorstore"""
        if self._vectorstore is None:
            logger.info("Loading Pinecone vectorstore...")
            embedding = Embedding(
                model_name="BAAI/bge-m3",
                index_name=self.index_name,
                pinecone_api_key=self.pinecone_api_key,
            )
            self._vectorstore = embedding.load_embedding()
            logger.info("Vectorstore loaded!")
        return self._vectorstore

    @property
    def splits(self):
        """Lazy load document splits for BM25"""
        if self._splits is None:
            logger.info("Loading corpus for BM25...")
            _, self._splits = load_corpus(self.corpus_path)
            logger.info(f"Loaded {len(self._splits)} document chunks")
        return self._splits

    @property
    def search_engine(self):
        """Lazy load hybrid search engine"""
        if self._search_engine is None:
            logger.info("Initializing hybrid search engine...")
            self._search_engine = Searching(
                k1=5,  # TUNED: Reduced from 10 to 5 for better precision
                k2=5,  # TUNED: Reduced from 10 to 5 for better precision
                embedding_instance=self.vectorstore,
                splits=self.splits,
            )
            logger.info("Search engine ready!")
        return self._search_engine

    @property
    def llm(self):
        """Lazy load LLM - Using Gemini API"""
        if self._llm is None:
            logger.info("Initializing LLM (Gemini)...")
            self._llm = LLM(
                model_name="models/gemini-2.5-flash",
                temperature=0.4,
                language="vi",
            )
            logger.info("LLM ready!")
        return self._llm

    @property
    def reranker(self):
        """Lazy load reranker"""
        if self._reranker is None and self.use_reranker:
            logger.info(f"Initializing reranker ({self.reranker_model})...")
            try:
                self._reranker = Reranker(model_name=self.reranker_model, top_n=5)
                logger.info("Reranker ready!")
            except Exception as e:
                logger.warning(f"Reranker initialization failed: {e}")
                logger.warning("   Continuing without reranker...")
                self.use_reranker = False
        return self._reranker

    def retrieve_context(self, query, top_k=5, search_type="hybrid", use_reranker=None):
        """
        OPTIMIZED: Optimized reranking

        Args:
            query: User query
            top_k: Final number of documents (default: 5)
            search_type: 'hybrid', 'vector', or 'bm25'
            use_reranker: Override class setting

        Returns:
            list: Retrieved and cleaned document contents
        """
        try:
            logger.info(f"Retrieving (top-{top_k})...")

            # Reduce candidate count
            should_rerank = (
                use_reranker if use_reranker is not None else self.use_reranker
            )
            initial_k = top_k * 2 if should_rerank else top_k

            # Search
            if search_type == "hybrid":
                docs = self.search_engine.hybrid_search(query)
            elif search_type == "vector":
                docs = self.search_engine.vector_search(query)
            elif search_type == "bm25":
                docs = self.search_engine.bm25_search(query)
            else:
                docs = self.search_engine.hybrid_search(query)

            # Extract content
            context_candidates = self.search_engine.get_context(docs[:initial_k])
            logger.info(f"   Retrieved {len(context_candidates)} candidates")

            # Rerank if enabled
            final_context = context_candidates
            if should_rerank and self.reranker:
                logger.info(f"Reranking to top-{top_k}...")
                try:
                    # TUNED: Pass threshold to filter low-score docs
                    final_context = self.reranker.rerank(
                        query, context_candidates, threshold=0.3
                    )
                    logger.info("   Reranked")
                except Exception as e:
                    logger.warning(f"   Reranking failed: {e}")
                    final_context = context_candidates[:top_k]
            else:
                final_context = context_candidates[:top_k]

            # Clean and return
            cleaned_context = preprocess_context(final_context)
            logger.info(f"Final: {len(cleaned_context)} documents")

            return cleaned_context

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            import traceback

            traceback.print_exc()
            return []

    def generate_answer(
        self,
        query,
        conversation_history=None,
        use_rag=True,
        include_context_in_response=False,
    ):
        """Generate answer using RAG pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("RAG PIPELINE")
            logger.info("=" * 60)

            # Retrieve context if enabled
            context_docs = []
            if use_rag:
                logger.info(f"Query: {query[:50]}...")
                context_docs = self.retrieve_context(
                    query, top_k=5, search_type="hybrid"
                )

            # Build context string
            context_str = None
            if context_docs and len(context_docs) > 0:
                context_str = "\n\n".join(
                    [f"[Document {i+1}]:\n{doc}" for i, doc in enumerate(context_docs)]
                )
                logger.info(f"Context: {len(context_docs)} docs")
            else:
                logger.warning("No context found")

            # Generate
            logger.info("Generating...")
            llm_instance = self.llm
            prompt = llm_instance.preprocess_prompt(question=query, context=context_str)
            answer = llm_instance.generate(prompt)

            logger.info("Done!")
            logger.info("=" * 60)

            result = {"answer": answer, "has_context": len(context_docs) > 0}

            if include_context_in_response:
                result["context_used"] = context_docs

            return result

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            import traceback

            traceback.print_exc()

            return {
                "answer": "Xin loi, toi dang gap su co ky thuat. Vui long thu lai sau.",
                "context_used": [] if include_context_in_response else None,
                "has_context": False,
            }


# ==========================================
# Global Singleton Instance
# ==========================================
_rag_service_instance = None


def get_rag_service(use_reranker=True, reranker_model="BAAI/bge-reranker-v2-m3"):
    """Get or create RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService(
            use_reranker=use_reranker, reranker_model=reranker_model
        )
    return _rag_service_instance


# ==========================================
# Wrapper for chat_controller.py
# ==========================================
def call_rag_gemini(messages):
    """
    Wrapper function for Flask - Uses AGENT
    """
    try:
        from backend.routes.agents.medical_agent_with_toolcall import chat_with_agent

        return chat_with_agent(messages)

    except Exception as e:
        logger.error(f"Error in call_rag_gemini: {e}")
        import traceback

        traceback.print_exc()
        return "Xin loi, toi dang gap su co ky thuat. Vui long thu lai sau."
