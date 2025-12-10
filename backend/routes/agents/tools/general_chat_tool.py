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
# Input Schema
# ==========================================
class GeneralChatInput(BaseModel):
    """Input schema for general chat"""

    query: str = Field(
        description="Cau hoi hoac noi dung tro chuyen thong thuong cua nguoi dung. "
        "Vi du: 'xin chao', 'ban ten gi', 'hom nay the nao'"
    )


# ==========================================
# General Chat Function
# ==========================================
def general_chat(query: str) -> str:
    """
    Handle general conversation using LLM with professional personality.

    Use this tool when:
    - User asks casual questions (greetings, small talk)
    - Questions about the bot itself ("ban la ai?", "ban lam gi?")
    - General chitchat not related to medical or calculations
    - Expressions of thanks, goodbye, etc.
    - Weather, food, travel, entertainment questions

    Do NOT use for:
    - Medical questions (use search_medical_documents)
    - Math calculations (use calculator)

    Examples:
    - "xin chao" -> Use this tool
    - "ban ten gi?" -> Use this tool
    - "cam on" -> Use this tool
    - "thoi tiet hom nay" -> Use this tool
    - "dau dau" -> Do NOT use (medical)
    - "2 + 2" -> Do NOT use (math)

    Args:
        query: User's casual question

    Returns:
        str: Friendly conversational response
    """
    try:
        print(f"\nGENERAL CHAT TOOL CALLED")
        print(f"   Query: {query}")

        # Import LLM (lazy loading)
        from backend.routes.rag.llms import LLM

        # Initialize LLM for chat with higher temperature for natural conversation
        llm = LLM(
            model_name="models/gemini-2.5-flash",
            temperature=0.7,  # Higher temp for more natural, creative chat
            language="vi",
        )

        # Build professional chat prompt with personality
        chat_prompt = f"""Ban la VieMedChat - tro ly AI y te than thien va chuyen nghiep.

TINH CACH:
- Than thien, nhiet tinh, luon san sang giup do
- Chuyen nghiep nhung khong cung nhac
- Biet lang nghe va thau hieu
- Tra loi ngan gon, tu nhien (1-3 cau)

VAI TRO:
Ban la tro ly AI chuyen ve y te, co the:
- Tu van ve trieu chung, benh ly, thuoc men
- Tinh toan cac chi so suc khoe (BMI, v.v.)
- Tro chuyen than thien ve cac chu de thuong ngay

NGUON DU LIEU:
- Du lieu y te duoc thu thap tu Benh vien Da khoa Tam Anh
- Co so du lieu chuyen sau ve cac benh ly, trieu chung, va dieu tri

NGUOI DUNG NOI:
"{query}"

HUONG DAN TRA LOI:

1. Neu chao hoi (xin chao, hi, hello):
   Tra loi: "Xin chao! Toi la VieMedChat, tro ly AI y te. Toi co the giup gi cho ban hom nay?"

2. Neu hoi ve ban than (ban la ai, ten gi, lam gi):
   Tra loi: "Toi la VieMedChat, tro ly AI chuyen ve y te. Toi co the giup ban tu van ve suc khoe, trieu chung benh, thuoc men, va cac van de y te khac!"

3. Neu hoi ve kha nang/tool (ban co the lam gi, co nhung tool nao):
   Tra loi: "Toi co 3 cong cu chinh:
   - Tim kiem thong tin y te (trieu chung, benh, thuoc)
   - Tinh toan chi so suc khoe (BMI, v.v.)
   - Tro chuyen tu van than thien
   Ban can toi giup gi nhe?"

4. Neu hoi ve nguon du lieu (du lieu tu dau, thu thap o dau):
   Tra loi: "Du lieu y te cua toi duoc thu thap tu Benh vien Da khoa Tam Anh, mot trong nhung benh vien uy tin hang dau Viet Nam. Toi co the giup ban tim hieu ve cac van de suc khoe dua tren nguon thong tin nay!"

5. Neu cam on (cam on, thanks):
   Tra loi: "Rat vui duoc giup do ban! Neu co thac mac gi ve suc khoe, dung ngai hoi nhe!"

6. Neu tam biet (bye, tam biet):
   Tra loi: "Tam biet! Chuc ban luon khoe manh! Hen gap lai!"

7. Neu hoi thoi tiet:
   Tra loi: "Toi khong co kha nang xem thoi tiet, nhung toi co the tu van ve suc khoe cho ban! Ban co cau hoi gi ve y te khong?"

8. Neu hoi mon an/du lich/giai tri:
   Tra loi: "Do la chu de thu vi! Tuy nhien, toi chuyen ve y te hon. Nhung neu ban can tu van dinh duong hoac che do an uong cho suc khoe, toi rat san long giup do!"

9. Neu tro chuyen chung chung:
   Tra loi than thien, tu nhien, nhung nhe nhang dan dat ve chu de y te

LUU Y QUAN TRONG:
- Tra loi NGAN GON (1-3 cau)
- Tu nhien, khong rap khuon
- Luon the hien su than thien
- Nhe nhang nhac ve vai tro tro ly y te
- KHONG nhac den Google, mo hinh ngon ngu, hay cong nghe AI
- Chi noi ve nguon du lieu tu Benh vien Tam Anh khi duoc hoi

Hay tra loi:"""

        # Generate response
        response = llm.generate(chat_prompt)

        print(f"   Response generated")

        return response.strip()

    except Exception as e:
        print(f"   Error in general_chat: {e}")
        import traceback

        traceback.print_exc()

        # Fallback responses
        query_lower = query.lower()

        if any(greeting in query_lower for greeting in ["chao", "hello", "hi", "hey"]):
            return "Xin chao! Toi la VieMedChat, tro ly AI y te. Toi co the giup gi cho ban hom nay?"

        elif any(thanks in query_lower for thanks in ["cam on", "thank", "thanks"]):
            return (
                "Rat vui duoc giup do ban! Neu co cau hoi gi khac, dung ngai hoi nhe!"
            )

        elif any(bye in query_lower for bye in ["tam biet", "bye", "goodbye"]):
            return "Tam biet! Chuc ban mot ngay tot lanh!"

        elif "ten" in query_lower or "la ai" in query_lower:
            return "Toi la VieMedChat, tro ly AI y te, duoc thiet ke de giup ban tu van ve cac van de suc khoe."

        else:
            return "Toi la VieMedChat, tro ly AI y te. Ban co cau hoi gi ve suc khoe khong? Toi san sang ho tro!"


# ==========================================
# LangChain Tool Definition
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
            Cong cu tro chuyen thong thuong, xu ly cac cau hoi chung chung.
            
            SU DUNG khi:
            - Cau chao hoi (xin chao, hi, hello)
            - Cau hoi ve bot (ban la ai, ten gi, lam gi)
            - Cam on, tam biet
            - Hoi thoi tiet, mon an, du lich, giai tri
            - Tro chuyen thong thuong, khong lien quan y te hoac tinh toan
            
            KHONG SU DUNG khi:
            - Cau hoi y te (trieu chung, benh, thuoc) -> dung search_medical_documents
            - Phep tinh toan hoc -> dung calculator
            
            Vi du su dung:
            - "xin chao" -> general_chat("xin chao")
            - "ban ten gi?" -> general_chat("ban ten gi?")
            - "cam on ban" -> general_chat("cam on ban")
            - "thoi tiet hom nay" -> general_chat("thoi tiet hom nay")
            
            Input: Cau hoi chung (string)
            Output: Cau tra loi than thien, chuyen nghiep
        """,
        args_schema=GeneralChatInput,
        return_direct=False,
    )
