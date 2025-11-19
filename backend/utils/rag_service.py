# # utils/rag_service.py - Complete RAG Pipeline with Reranker
# import os
# from dotenv import load_dotenv

# # Import RAG components
# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# from backend.routes.rag.embedding import Embedding
# from backend.routes.rag.search import Searching
# from backend.routes.rag.utils import load_corpus, preprocess_context
# from backend.routes.rag.llms import LLM
# from backend.routes.rag.reranker import Reranker

# load_dotenv()


# class RAGService:
#     """
#     Complete RAG Pipeline for Medical Chatbot
    
#     Pipeline Flow:
#     1. User Query → 2. Hybrid Search (BM25 + Vector) → 3. Reranker → 4. LLM Generation
#     """
    
#     def __init__(self, use_reranker=True, reranker_model="BAAI/bge-reranker-v2-m3"):
#         """
#         Initialize complete RAG pipeline
        
#         Args:
#             use_reranker: Enable/disable reranker (default: True)
#             reranker_model: "BAAI/bge-reranker-v2-m3" or "cohere"
#         """
#         # API Keys
#         self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
#         self.google_api_key = os.getenv("GOOGLE_API_KEY")
#         self.cohere_api_key = os.getenv("COHERE_API_KEY")
        
#         # Configs
#         self.index_name = os.getenv("PINECONE_INDEX_NAME")
#         self.corpus_path = os.getenv("CORPUS_PATH")
#         self.use_reranker = use_reranker
#         self.reranker_model = reranker_model
        
#         # Lazy loading attributes
#         self._vectorstore = None
#         self._search_engine = None
#         self._splits = None
#         self._llm = None
#         self._reranker = None
        
#         print("🤖 RAG Service initialized (lazy loading enabled)")
#         print(f"   - Reranker: {'✅ Enabled' if use_reranker else '❌ Disabled'}")
    
#     @property
#     def vectorstore(self):
#         """Lazy load Pinecone vectorstore"""
#         if self._vectorstore is None:
#             print("📦 Loading Pinecone vectorstore...")
#             embedding = Embedding(
#                 model_name="BAAI/bge-m3",
#                 index_name=self.index_name,
#                 pinecone_api_key=self.pinecone_api_key
#             )
#             self._vectorstore = embedding.load_embedding()
#             print("✅ Vectorstore loaded!")
#         return self._vectorstore
    
#     @property
#     def splits(self):
#         """Lazy load document splits for BM25"""
#         if self._splits is None:
#             print("📚 Loading corpus for BM25...")
#             _, self._splits = load_corpus(self.corpus_path)
#             print(f"✅ Loaded {len(self._splits)} document chunks")
#         return self._splits
    
#     @property
#     def search_engine(self):
#         """Lazy load hybrid search engine"""
#         if self._search_engine is None:
#             print("🔍 Initializing hybrid search engine...")
#             self._search_engine = Searching(
#                 k1=10,
#                 k2=10,
#                 embedding_instance=self.vectorstore,
#                 splits=self.splits
#             )
#             print("✅ Search engine ready!")
#         return self._search_engine
    
#     @property
#     def llm(self):
#         """Lazy load LLM"""
#         if self._llm is None:
#             print("🤖 Initializing LLM...")
#             self._llm = LLM(
#                 groq_api_key=os.getenv("GROQ_API_KEY"),
#                 model_name="groq/llama-3.3-70b-versatile",
#                 temperature=0.4,
#                 language="vi"
#             )
#             print("✅ LLM ready!")
#         return self._llm
    
#     @property
#     def reranker(self):
#         """Lazy load reranker"""
#         if self._reranker is None and self.use_reranker:
#             print(f"🎯 Initializing reranker ({self.reranker_model})...")
#             try:
#                 self._reranker = Reranker(
#                     model_name=self.reranker_model,
#                     top_n=5
#                 )
#                 print("✅ Reranker ready!")
#             except Exception as e:
#                 print(f"⚠️ Reranker initialization failed: {e}")
#                 print("   Continuing without reranker...")
#                 self.use_reranker = False
#         return self._reranker
    
#     def retrieve_context(self, query, top_k=5, search_type="hybrid", use_reranker=None):
#         """
#         Retrieve relevant context with optional reranking
        
#         Pipeline:
#         1. Hybrid Search (BM25 + Vector) → get top 10-15 candidates
#         2. Reranker → rerank to top 3-5 most relevant
#         3. Return cleaned context
        
#         Args:
#             query: User query
#             top_k: Final number of documents to return
#             search_type: 'hybrid', 'vector', or 'bm25'
#             use_reranker: Override class setting (None = use class setting)
        
#         Returns:
#             list: Retrieved and cleaned document contents
#         """
#         try:
#             # Step 1: Retrieve candidates with search
#             print(f"\n🔍 Step 1: Retrieving candidates with {search_type} search...")
            
#             # Get more candidates for reranking
#             initial_k = top_k * 2 if (use_reranker if use_reranker is not None else self.use_reranker) else top_k
            
#             if search_type == "hybrid":
#                 docs = self.search_engine.hybrid_search(query)
#             elif search_type == "vector":
#                 docs = self.search_engine.vector_search(query)
#             elif search_type == "bm25":
#                 docs = self.search_engine.bm25_search(query)
#             else:
#                 docs = self.search_engine.hybrid_search(query)
            
#             # Extract content
#             context_candidates = self.search_engine.get_context(docs[:initial_k])
#             print(f"   Retrieved {len(context_candidates)} candidates")
            
#             # Step 2: Rerank if enabled
#             final_context = context_candidates
#             if (use_reranker if use_reranker is not None else self.use_reranker) and self.reranker:
#                 print(f"\n🎯 Step 2: Reranking with {self.reranker_model}...")
#                 try:
#                     final_context = self.reranker.rerank(query, context_candidates)
#                     print(f"   Reranked to top {len(final_context)} documents")
#                 except Exception as e:
#                     print(f"   ⚠️ Reranking failed: {e}, using original results")
#                     final_context = context_candidates[:top_k]
#             else:
#                 final_context = context_candidates[:top_k]
            
#             # Step 3: Clean and return
#             cleaned_context = preprocess_context(final_context)
#             print(f"\n✅ Final: {len(cleaned_context)} relevant documents")
            
#             return cleaned_context
            
#         except Exception as e:
#             print(f"❌ Error retrieving context: {e}")
#             import traceback
#             traceback.print_exc()
#             return []
    
#     def generate_answer(self, query, conversation_history=None, use_rag=True, 
#                    include_context_in_response=False):
#         """
#         Generate answer using complete RAG pipeline
        
#         Pipeline:
#         1. Retrieve context (Hybrid Search + Reranker)
#         2. Build prompt with context + history
#         3. Generate with LLM
        
#         Args:
#             query: User query
#             conversation_history: Previous messages [{'role': 'user'/'assistant', 'content': '...'}]
#             use_rag: Whether to use RAG context
#             include_context_in_response: Return context docs in response
        
#         Returns:
#             dict: {
#                 'answer': str,
#                 'context_used': list (if include_context_in_response=True),
#                 'has_context': bool
#             }
#         """
#         try:
#             print("\n" + "="*60)
#             print("🚀 RAG PIPELINE STARTING")
#             print("="*60)
            
#             # Step 1: Retrieve context if enabled
#             context_docs = []
#             if use_rag:
#                 print(f"📝 Query: {query}")
#                 context_docs = self.retrieve_context(
#                     query, 
#                     top_k=3,
#                     search_type="hybrid"
#                 )
            
#             # Step 2: Build context string
#             context_str = None
#             if context_docs and len(context_docs) > 0:
#                 context_str = "\n\n".join([
#                     f"[Tài liệu {i+1}]:\n{doc}" 
#                     for i, doc in enumerate(context_docs)
#                 ])
#                 print(f"\n📚 Context prepared ({len(context_docs)} documents)")
#             else:
#                 print("\n⚠️ No relevant context found")
            
#             # Step 3: Get LLM instance and build prompt
#             print("\n🤖 Building prompt and generating...")
            
#             llm_instance = self.llm
            
#             prompt = llm_instance.preprocess_prompt(
#                 question=query,
#                 context=context_str
#             )
            
#             # Step 4: Generate answer
#             answer = llm_instance.generate(prompt)
            
#             print("\n✅ Answer generated successfully!")
#             print("="*60 + "\n")
            
#             result = {
#                 'answer': answer,
#                 'has_context': len(context_docs) > 0
#             }
            
#             if include_context_in_response:
#                 result['context_used'] = context_docs
            
#             return result
            
#         except Exception as e:
#             print(f"\n❌ Error in RAG pipeline: {e}")
#             import traceback
#             traceback.print_exc()
            
#             return {
#                 'answer': "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
#                 'context_used': [] if include_context_in_response else None,
#                 'has_context': False
#             }
    
#     def chat(self, query, conversation_history=None):
#         """
#         Simple chat interface (alternative to generate_answer)
        
#         Args:
#             query: User question
#             conversation_history: List of previous messages
        
#         Returns:
#             str: Generated answer
#         """
#         result = self.generate_answer(
#             query=query,
#             conversation_history=conversation_history,
#             use_rag=True,
#             include_context_in_response=False
#         )
#         return result['answer']


# # ==========================================
# # 🎯 Global Singleton Instance
# # ==========================================
# _rag_service_instance = None

# def get_rag_service(use_reranker=True, reranker_model="BAAI/bge-reranker-v2-m3"):
#     """
#     Get or create RAG service singleton
    
#     Args:
#         use_reranker: Enable reranker (default: True)
#         reranker_model: "BAAI/bge-reranker-v2-m3" or "cohere"
#     """
#     global _rag_service_instance
#     if _rag_service_instance is None:
#         _rag_service_instance = RAGService(
#             use_reranker=use_reranker,
#             reranker_model=reranker_model
#         )
#     return _rag_service_instance


# # ==========================================
# # 🔌 Wrapper for chat_controller.py
# # ==========================================
# def call_rag_gemini(messages):
#     """
#     Simple wrapper function for Flask chat_controller
#     NOW USES LANGCHAIN AGENT!
    
#     Args:
#         messages: List of conversation messages [{'role': 'user'/'assistant', 'content': '...'}]
    
#     Returns:
#         str: Generated answer
#     """
#     try:
#         # ✅ LAZY IMPORT để tránh circular import
#         from backend.routes.agents.medical_agent import chat_with_agent
#         return chat_with_agent(messages)
        
#     except Exception as e:
#         print(f"❌ Error in call_rag_gemini: {e}")
#         import traceback
#         traceback.print_exc()
        
#         # Fallback to basic response
#         return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."

"""
Optimized RAG Service với caching và giảm số lượng retrieval
"""
import os
from dotenv import load_dotenv
from functools import lru_cache

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.routes.rag.embedding import Embedding
from backend.routes.rag.search import Searching
from backend.routes.rag.utils import load_corpus, preprocess_context
from backend.routes.rag.llms import LLM
from backend.routes.rag.reranker import Reranker

load_dotenv()


class RAGService:
    """
    Optimized RAG Pipeline với:
    - Giảm số lượng documents retrieve
    - Caching results
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
        
        print("🤖 RAG Service initialized (lazy loading enabled)")
        print(f"   - Reranker: {'✅ Enabled' if use_reranker else '❌ Disabled'}")
    
    @property
    def vectorstore(self):
        """Lazy load Pinecone vectorstore"""
        if self._vectorstore is None:
            print("📦 Loading Pinecone vectorstore...")
            embedding = Embedding(
                model_name="BAAI/bge-m3",
                index_name=self.index_name,
                pinecone_api_key=self.pinecone_api_key
            )
            self._vectorstore = embedding.load_embedding()
            print("✅ Vectorstore loaded!")
        return self._vectorstore
    
    @property
    def splits(self):
        """Lazy load document splits for BM25"""
        if self._splits is None:
            print("📚 Loading corpus for BM25...")
            _, self._splits = load_corpus(self.corpus_path)
            print(f"✅ Loaded {len(self._splits)} document chunks")
        return self._splits
    
    @property
    def search_engine(self):
        """Lazy load hybrid search engine"""
        if self._search_engine is None:
            print("🔍 Initializing hybrid search engine...")
            self._search_engine = Searching(
                k1=5,  # ✅ GIẢM từ 10 → 5 cho vector search
                k2=5,  # ✅ GIẢM từ 10 → 5 cho BM25
                embedding_instance=self.vectorstore,
                splits=self.splits
            )
            print("✅ Search engine ready!")
        return self._search_engine
    
    @property
    def llm(self):
        """Lazy load LLM - Using Ollama"""
        if self._llm is None:
            print("🤖 Initializing LLM (Ollama)...")
            self._llm = LLM(
                model_name="ollama/qwen2.5:7b",  # ✅ SỬ DỤNG OLLAMA
                ollama_url="http://localhost:11434",
                temperature=0.4,
                language="vi"
            )
            print("✅ LLM ready!")
        return self._llm
    
    @property
    def reranker(self):
        """Lazy load reranker"""
        if self._reranker is None and self.use_reranker:
            print(f"🎯 Initializing reranker ({self.reranker_model})...")
            try:
                self._reranker = Reranker(
                    model_name=self.reranker_model,
                    top_n=5 
                )
                print("✅ Reranker ready!")
            except Exception as e:
                print(f"⚠️ Reranker initialization failed: {e}")
                print("   Continuing without reranker...")
                self.use_reranker = False
        return self._reranker
    
    def retrieve_context(self, query, top_k=5, search_type="hybrid", use_reranker=None):
        """
        ✅ OPTIMIZED: Tối ưu reranking
        
        Args:
            query: User query
            top_k: Final number of documents (default: 5)
            search_type: 'hybrid', 'vector', or 'bm25'
            use_reranker: Override class setting
        
        Returns:
            list: Retrieved and cleaned document contents
        """
        try:
            print(f"\n🔍 Retrieving (top-{top_k})...")
            
            # ✅ Giảm số lượng candidates
            should_rerank = use_reranker if use_reranker is not None else self.use_reranker
            initial_k = top_k * 2 if should_rerank else top_k  # 6 thay vì 10-15
            
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
            print(f"   Retrieved {len(context_candidates)} candidates")
            
            # Rerank if enabled
            final_context = context_candidates
            if should_rerank and self.reranker:
                print(f"\n🎯 Reranking to top-{top_k}...")
                try:
                    final_context = self.reranker.rerank(query, context_candidates)
                    print(f"   ✅ Reranked")
                except Exception as e:
                    print(f"   ⚠️ Reranking failed: {e}")
                    final_context = context_candidates[:top_k]
            else:
                final_context = context_candidates[:top_k]
            
            # Clean and return
            cleaned_context = preprocess_context(final_context)
            print(f"\n✅ Final: {len(cleaned_context)} documents")
            
            return cleaned_context
            
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_answer(self, query, conversation_history=None, use_rag=True, 
                   include_context_in_response=False):
        """Generate answer using RAG pipeline"""
        try:
            print("\n" + "="*60)
            print("🚀 RAG PIPELINE")
            print("="*60)
            
            # Retrieve context if enabled
            context_docs = []
            if use_rag:
                print(f"📝 Query: {query[:50]}...")
                context_docs = self.retrieve_context(
                    query, 
                    top_k=5,  
                    search_type="hybrid"
                )
            
            # Build context string
            context_str = None
            if context_docs and len(context_docs) > 0:
                context_str = "\n\n".join([
                    f"[Tài liệu {i+1}]:\n{doc[:500]}"  # ✅ Cắt ngắn mỗi doc
                    for i, doc in enumerate(context_docs)
                ])
                print(f"\n📚 Context: {len(context_docs)} docs")
            else:
                print("\n⚠️ No context")
            
            # Generate
            print("\n🤖 Generating...")
            llm_instance = self.llm
            prompt = llm_instance.preprocess_prompt(
                question=query,
                context=context_str
            )
            answer = llm_instance.generate(prompt)
            
            print("\n✅ Done!")
            print("="*60 + "\n")
            
            result = {
                'answer': answer,
                'has_context': len(context_docs) > 0
            }
            
            if include_context_in_response:
                result['context_used'] = context_docs
            
            return result
            
        except Exception as e:
            print(f"\n❌ Error in RAG pipeline: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'answer': "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                'context_used': [] if include_context_in_response else None,
                'has_context': False
            }


# ==========================================
# 🎯 Global Singleton Instance
# ==========================================
_rag_service_instance = None

def get_rag_service(use_reranker=True, reranker_model="BAAI/bge-reranker-v2-m3"):
    """Get or create RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService(
            use_reranker=use_reranker,
            reranker_model=reranker_model
        )
    return _rag_service_instance


# ==========================================
# 🔌 Wrapper for chat_controller.py
# ==========================================
def call_rag_gemini(messages):
    """
    Wrapper function for Flask - SỬ DỤNG AGENT
    """
    try:
        from backend.routes.agents.medical_agent import chat_with_agent
        return chat_with_agent(messages)
        
    except Exception as e:
        print(f"❌ Error in call_rag_gemini: {e}")
        import traceback
        traceback.print_exc()
        return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."