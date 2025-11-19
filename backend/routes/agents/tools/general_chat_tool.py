"""
General Chat Tool for LangChain Agent
Handles casual conversation using LLM
"""
from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


# ==========================================
# 📊 Input Schema
# ==========================================
class GeneralChatInput(BaseModel):
    """Input schema for general chat"""
    query: str = Field(
        description="Câu hỏi hoặc nội dung trò chuyện thông thường của người dùng. "
                    "Ví dụ: 'xin chào', 'bạn tên gì', 'hôm nay thế nào'"
    )


# ==========================================
# 💬 General Chat Function
# ==========================================
def general_chat(query: str) -> str:
    """
    Handle general conversation using LLM.
    
    Use this tool when:
    - User asks casual questions (greetings, small talk)
    - Questions about the bot itself ("bạn là ai?", "bạn làm gì?")
    - General chitchat not related to medical or calculations
    - Expressions of thanks, goodbye, etc.
    
    Do NOT use for:
    - Medical questions (use search_medical_documents)
    - Math calculations (use calculator)
    
    Examples:
    - "xin chào" → Use this tool
    - "bạn tên gì?" → Use this tool
    - "cảm ơn" → Use this tool
    - "đau đầu" → Do NOT use (medical)
    - "2 + 2" → Do NOT use (math)
    
    Args:
        query: User's casual question
    
    Returns:
        str: Friendly conversational response
    """
    try:
        print(f"\n💬 GENERAL CHAT TOOL CALLED")
        print(f"   Query: {query}")
        
        # Import LLM (lazy loading)
        from backend.routes.rag.llms import LLM
        
        # Initialize LLM for chat
        llm = LLM(
            # model_name="ollama/qwen2.5:7b",  # Fast small model for chat
            model_name="gemini-1.5-flash",
            # ollama_url="http://localhost:11434",
            temperature=0.4,  # Higher temp for more creative chat
            language="vi"
        )
        
        # Build casual chat prompt
        chat_prompt = f"""Bạn là một trợ lý AI thân thiện và nhiệt tình.

Người dùng nói: "{query}"

Hãy trả lời một cách ngắn gọn, tự nhiên và thân thiện (1-2 câu).

Lưu ý:
- Nếu được hỏi về bản thân: "Tôi là trợ lý AI y tế, có thể giúp bạn tư vấn về sức khỏe"
- Nếu được cảm ơn: "Rất vui được giúp đỡ bạn!"
- Nếu được chào: "Xin chào! Tôi có thể giúp gì cho bạn?"
- Nếu tạm biệt: "Chúc bạn một ngày tốt lành!"

Trả lời:"""
        
        # Generate response
        response = llm.generate(chat_prompt)
        
        print(f"   ✅ Response generated")
        
        return response.strip()
        
    except Exception as e:
        print(f"   ❌ Error in general_chat: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback responses
        query_lower = query.lower()
        
        if any(greeting in query_lower for greeting in ['chào', 'hello', 'hi', 'hey']):
            return "Xin chào! Tôi là trợ lý AI y tế. Tôi có thể giúp gì cho bạn hôm nay?"
        
        elif any(thanks in query_lower for thanks in ['cảm ơn', 'thank', 'thanks']):
            return "Rất vui được giúp đỡ bạn! Nếu có câu hỏi gì khác, đừng ngại hỏi nhé!"
        
        elif any(bye in query_lower for bye in ['tạm biệt', 'bye', 'goodbye']):
            return "Tạm biệt! Chúc bạn một ngày tốt lành! 👋"
        
        elif 'tên' in query_lower or 'là ai' in query_lower:
            return "Tôi là trợ lý AI y tế, được thiết kế để giúp bạn tư vấn về các vấn đề sức khỏe."
        
        else:
            return "Tôi là trợ lý AI y tế. Bạn có câu hỏi gì về sức khỏe không? Tôi sẵn sàng hỗ trợ!"


# ==========================================
# 🛠️ LangChain Tool Definition
# ==========================================
def get_general_chat_tool():
    """
    Get general chat tool for LangChain agent
    
    Returns:
        Tool: LangChain Tool object
    """
    return Tool(
        name="general_chat",
        func=general_chat,
        description="""
            Công cụ trò chuyện thông thường, xử lý các câu hỏi chung chung.
            
            SỬ DỤNG khi:
            - Câu chào hỏi (xin chào, hi, hello)
            - Câu hỏi về bot (bạn là ai, tên gì, làm gì)
            - Cảm ơn, tạm biệt
            - Trò chuyện thông thường, không liên quan y tế hoặc tính toán
            
            KHÔNG SỬ DỤNG khi:
            - Câu hỏi y tế (triệu chứng, bệnh, thuốc) → dùng search_medical_documents
            - Phép tính toán học → dùng calculator
            
            Ví dụ sử dụng:
            - "xin chào" → general_chat("xin chào")
            - "bạn tên gì?" → general_chat("bạn tên gì?")
            - "cảm ơn bạn" → general_chat("cảm ơn bạn")
            
            Input: Câu hỏi chung (string)
            Output: Câu trả lời thân thiện
        """,
        args_schema=GeneralChatInput,
        return_direct=False
    )