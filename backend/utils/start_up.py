"""
Startup hook to pre-initialize heavy components
Runs once when Flask server starts
"""
import os
from dotenv import load_dotenv
from utils.rag_service import get_rag_service

load_dotenv()


def initialize_rag_components():
    """
    Pre-load all heavy components on startup:
    - Embedding model (1024-dim, ~500MB)
    - Pinecone index connection
    - BM25 corpus (24k documents)
    - Reranker model
    
    This runs ONCE when server starts, not per-request.
    """
    print("\n" + "="*60)
    print("🚀 PRE-INITIALIZING RAG COMPONENTS")
    print("="*60)
    
    try:
        # Get RAG service singleton
        rag = get_rag_service(use_reranker=True)
        
        # Force initialization of all lazy-loaded components
        print("\n1️⃣ Loading Embedding Model & Pinecone...")
        _ = rag.vectorstore  # Triggers embedding model load
        
        print("\n2️⃣ Loading BM25 Corpus...")
        _ = rag.splits  # Triggers corpus load
        
        print("\n3️⃣ Initializing Search Engine...")
        _ = rag.search_engine  # Triggers search setup
        
        print("\n4️⃣ Loading Reranker...")
        _ = rag.reranker  # Triggers reranker load
        
        print("\n5️⃣ Loading LLM Client...")
        _ = rag.llm  # Triggers LLM client setup
        
        print("\n" + "="*60)
        print("✅ ALL COMPONENTS PRE-LOADED SUCCESSFULLY!")
        print("="*60)
        print("💡 Future requests will use cached components")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during pre-initialization: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️ Server will start but components will lazy-load per request")
        return False


def warmup_test():
    """
    Optional: Run a test query to verify everything works
    """
    print("\n🧪 Running warmup test query...")
    
    try:
        rag = get_rag_service()
        result = rag.generate_answer(
            query="Xin chào",
            use_rag=False,  # Don't retrieve context for warmup
            include_context_in_response=False
        )
        
        if result['answer']:
            print("✅ Warmup test passed!")
            return True
        else:
            print("⚠️ Warmup test returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Warmup test failed: {e}")
        return False


if __name__ == "__main__":
    # For testing
    initialize_rag_components()
    warmup_test()