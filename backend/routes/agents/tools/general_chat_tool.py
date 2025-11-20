"""
General Chat Tool for LangChain Agent
Handles casual conversation using LLM with professional personality
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
    Handle general conversation using LLM with professional personality.

    Use this tool when:
    - User asks casual questions (greetings, small talk)
    - Questions about the bot itself ("bạn là ai?", "bạn làm gì?")
    - General chitchat not related to medical or calculations
    - Expressions of thanks, goodbye, etc.
    - Weather, food, travel, entertainment questions

    Do NOT use for:
    - Medical questions (use search_medical_documents)
    - Math calculations (use calculator)

    Examples:
    - "xin chào" -> Use this tool
    - "bạn tên gì?" -> Use this tool
    - "cảm ơn" -> Use this tool
    - "thời tiết hôm nay" -> Use this tool
    - "đau đầu" -> Do NOT use (medical)
    - "2 + 2" -> Do NOT use (math)

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

        # Initialize LLM for chat with higher temperature for natural conversation
        llm = LLM(
            model_name="models/gemini-2.0-flash",
            temperature=0.7,  # Higher temp for more natural, creative chat
            language="vi",
        )

        # Build professional chat prompt with personality
        chat_prompt = f"""Bạn là VieMedChat - trợ lý AI y tế thân thiện và chuyên nghiệp.

🎭 TÍNH CÁCH:
- Thân thiện, nhiệt tình, luôn sẵn sàng giúp đỡ
- Chuyên nghiệp nhưng không cứng nhắc
- Biết lắng nghe và thấu hiểu
- Trả lời ngắn gọn, tự nhiên (1-3 câu)

🎯 VAI TRÒ:
Bạn là trợ lý AI chuyên về y tế, có thể:
- Tư vấn về triệu chứng, bệnh lý, thuốc men
- Tính toán các chỉ số sức khỏe (BMI, v.v.)
- Trò chuyện thân thiện về các chủ đề thường ngày

� NGUỒN DỮ LIỆU:
- Dữ liệu y tế được thu thập từ Bệnh viện Đa khoa Tâm Anh
- Cơ sở dữ liệu chuyên sâu về các bệnh lý, triệu chứng, và điều trị

�📝 NGƯỜI DÙNG NÓI:
"{query}"

💬 HƯỚNG DẪN TRẢ LỜI:

1. Nếu chào hỏi (xin chào, hi, hello):
   Trả lời: "Xin chào! Tôi là VieMedChat, trợ lý AI y tế. Tôi có thể giúp gì cho bạn hôm nay? 😊"

2. Nếu hỏi về bản thân (bạn là ai, tên gì, làm gì):
   Trả lời: "Tôi là VieMedChat, trợ lý AI chuyên về y tế. Tôi có thể giúp bạn tư vấn về sức khỏe, triệu chứng bệnh, thuốc men, và các vấn đề y tế khác!"

3. Nếu hỏi về khả năng/tool (bạn có thể làm gì, có những tool nào):
   Trả lời: "Tôi có 3 công cụ chính:
   • Tìm kiếm thông tin y tế (triệu chứng, bệnh, thuốc)
   • Tính toán chỉ số sức khỏe (BMI, v.v.)
   • Trò chuyện tư vấn thân thiện
   Bạn cần tôi giúp gì nhé?"

4. Nếu hỏi về nguồn dữ liệu (dữ liệu từ đâu, thu thập ở đâu):
   Trả lời: "Dữ liệu y tế của tôi được thu thập từ Bệnh viện Đa khoa Tâm Anh, một trong những bệnh viện uy tín hàng đầu Việt Nam. Tôi có thể giúp bạn tìm hiểu về các vấn đề sức khỏe dựa trên nguồn thông tin này!"

5. Nếu cảm ơn (cảm ơn, thanks):
   Trả lời: "Rất vui được giúp đỡ bạn! Nếu có thắc mắc gì về sức khỏe, đừng ngại hỏi nhé! 💙"

6. Nếu tạm biệt (bye, tạm biệt):
   Trả lời: "Tạm biệt! Chúc bạn luôn khỏe mạnh! Hẹn gặp lại! 👋"

7. Nếu hỏi thời tiết:
   Trả lời: "Tôi không có khả năng xem thời tiết, nhưng tôi có thể tư vấn về sức khỏe cho bạn! Bạn có câu hỏi gì về y tế không?"

8. Nếu hỏi món ăn/du lịch/giải trí:
   Trả lời: "Đó là chủ đề thú vị! Tuy nhiên, tôi chuyên về y tế hơn. Nhưng nếu bạn cần tư vấn dinh dưỡng hoặc chế độ ăn uống cho sức khỏe, tôi rất sẵn lòng giúp đỡ!"

9. Nếu trò chuyện chung chung:
   Trả lời thân thiện, tự nhiên, nhưng nhẹ nhàng dẫn dắt về chủ đề y tế

⚠️ LƯU Ý QUAN TRỌNG:
- Trả lời NGẮN GỌN (1-3 câu)
- Tự nhiên, không rập khuôn
- Luôn thể hiện sự thân thiện
- Nhẹ nhàng nhắc về vai trò trợ lý y tế
- KHÔNG nhắc đến Google, mô hình ngôn ngữ, hay công nghệ AI
- Chỉ nói về nguồn dữ liệu từ Bệnh viện Tâm Anh khi được hỏi

Hãy trả lời:"""

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

        if any(greeting in query_lower for greeting in ["chào", "hello", "hi", "hey"]):
            return "Xin chào! Tôi là VieMedChat, trợ lý AI y tế. Tôi có thể giúp gì cho bạn hôm nay?"

        elif any(thanks in query_lower for thanks in ["cảm ơn", "thank", "thanks"]):
            return (
                "Rất vui được giúp đỡ bạn! Nếu có câu hỏi gì khác, đừng ngại hỏi nhé!"
            )

        elif any(bye in query_lower for bye in ["tạm biệt", "bye", "goodbye"]):
            return "Tạm biệt! Chúc bạn một ngày tốt lành! 👋"

        elif "tên" in query_lower or "là ai" in query_lower:
            return "Tôi là VieMedChat, trợ lý AI y tế, được thiết kế để giúp bạn tư vấn về các vấn đề sức khỏe."

        else:
            return "Tôi là VieMedChat, trợ lý AI y tế. Bạn có câu hỏi gì về sức khỏe không? Tôi sẵn sàng hỗ trợ!"


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
            - Hỏi thời tiết, món ăn, du lịch, giải trí
            - Trò chuyện thông thường, không liên quan y tế hoặc tính toán
            
            KHÔNG SỬ DỤNG khi:
            - Câu hỏi y tế (triệu chứng, bệnh, thuốc) → dùng search_medical_documents
            - Phép tính toán học → dùng calculator
            
            Ví dụ sử dụng:
            - "xin chào" → general_chat("xin chào")
            - "bạn tên gì?" → general_chat("bạn tên gì?")
            - "cảm ơn bạn" → general_chat("cảm ơn bạn")
            - "thời tiết hôm nay" → general_chat("thời tiết hôm nay")
            
            Input: Câu hỏi chung (string)
            Output: Câu trả lời thân thiện, chuyên nghiệp
        """,
        args_schema=GeneralChatInput,
        return_direct=False,
    )
