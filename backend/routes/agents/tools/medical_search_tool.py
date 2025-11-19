"""
LangChain Tools for Medical Chatbot
Agent sẽ tự động chọn tool phù hợp
"""
from langchain.tools import Tool
from pydantic import BaseModel, Field  # ✅ FIX: Import từ pydantic v2
from typing import Optional
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from backend.utils.rag_service import get_rag_service


# ==========================================
# 📚 Input Schema cho Tools
# ==========================================
class MedicalSearchInput(BaseModel):
    """Input schema for medical document search"""
    query: str = Field(
        description="Câu hỏi y tế hoặc triệu chứng của bệnh nhân. "
                    "Ví dụ: 'đau đầu và sốt', 'triệu chứng COVID-19'"
    )


# ==========================================
# 🔍 Medical Search Tool
# ==========================================
def search_medical_documents(query: str) -> str:
    """
    Search medical documents for relevant information.
    
    Use this tool when:
    - User asks about symptoms, diseases, or medical conditions
    - User needs information about medications or treatments
    - User asks medical questions that require factual information
    
    Do NOT use for:
    - Simple greetings (xin chào, hi, hello)
    - Chitchat (bạn là ai, cảm ơn)
    - General conversation
    
    Args:
        query: Medical question or symptom description
    
    Returns:
        str: Relevant medical information from knowledge base
    """
    try:
        print(f"\n🔍 TOOL CALLED: search_medical_documents")
        print(f"   Query: {query}")
        
        # Get RAG service
        rag = get_rag_service(use_reranker=True)
        
        # Retrieve context only
        context_docs = rag.retrieve_context(
            query=query,
            top_k=3,
            search_type="hybrid"
        )
        
        if not context_docs or len(context_docs) == 0:
            return "Không tìm thấy thông tin y tế liên quan trong cơ sở dữ liệu."
        
        # Format context for LLM
        formatted_context = "\n\n".join([
            f"📄 Tài liệu {i+1}:\n{doc}"
            for i, doc in enumerate(context_docs)
        ])
        
        print(f"✅ Retrieved {len(context_docs)} documents")
        
        return f"""Thông tin y tế từ cơ sở dữ liệu:

{formatted_context}

Hãy sử dụng thông tin trên để trả lời câu hỏi của bệnh nhân một cách chính xác và dễ hiểu."""
        
    except Exception as e:
        print(f"❌ Error in search_medical_documents: {e}")
        return "Xin lỗi, đã có lỗi khi tìm kiếm thông tin y tế."


# ==========================================
# 🛠️ LangChain Tool Definitions
# ==========================================
def get_medical_tools():
    """
    Get list of tools for medical chatbot agent
    
    Returns:
        list: LangChain Tool objects
    """
    tools = [
        Tool(
            name="search_medical_documents",
            func=search_medical_documents,
            description="""
                Tìm kiếm thông tin y tế từ cơ sở tri thức.
                
                SỬ DỤNG khi:
                - Người dùng hỏi về triệu chứng, bệnh tật
                - Cần thông tin về thuốc, điều trị
                - Câu hỏi y tế cần thông tin chính xác
                
                KHÔNG SỬ DỤNG khi:
                - Chào hỏi đơn giản (xin chào, hi)
                - Cảm ơn, tạm biệt
                - Trò chuyện thông thường
                
                Input: Câu hỏi y tế (string)
                Output: Thông tin y tế liên quan
            """,
            args_schema=MedicalSearchInput,
            return_direct=False
        )
    ]
    
    return tools