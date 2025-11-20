"""
Optimized Startup Hook - Pre-initialize ALL heavy components
Runs ONCE when Flask server starts
"""

import os
from dotenv import load_dotenv
from utils.rag_service import get_rag_service

# from routes.agents.medical_agent import get_medical_agent
from routes.agents.medical_agent_with_toolcall import get_medical_agent_tool_calling

load_dotenv()


def initialize_rag_components():
    """
    Pre-load ALL heavy components on startup:
    - Embedding model (1024-dim, ~500MB) ✅
    - Pinecone index connection ✅
    - BM25 corpus (24k documents) ✅
    - Reranker model ✅
    - LLM client ✅
    - Agent instance ✅

    This runs ONCE when server starts, not per-request.
    """
    print("\n" + "=" * 60)
    print("🚀 PRE-INITIALIZING RAG COMPONENTS")
    print("=" * 60)

    try:
        # ==========================================
        # 1. Pre-load RAG Service Components
        # ==========================================
        rag = get_rag_service(use_reranker=True)

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

        # ==========================================
        # 2. Pre-load Agent (CRITICAL for speed!)
        # ==========================================
        print("\n6️⃣ Pre-loading Medical Agent...")
        agent = get_medical_agent_tool_calling(model_name="models/gemini-2.0-flash")

        # # Warm up agent with a test query
        # print("\n7️⃣ Warming up agent with test query...")
        # test_result = agent.chat(
        #     query="xin chào",
        #     chat_history=[]
        # )
        # if test_result['answer']:
        #     print("   ✅ Agent warmup successful!")

        print("\n" + "=" * 60)
        print("✅ ALL COMPONENTS PRE-LOADED SUCCESSFULLY!")
        print("=" * 60)
        print("💡 Future requests will use cached components")
        print("💡 Expected response time: 2-5 seconds (down from 15-20s)")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ ERROR during pre-initialization: {e}")
        import traceback

        traceback.print_exc()
        print("\n⚠️ Server will start but components will lazy-load per request")
        return False
