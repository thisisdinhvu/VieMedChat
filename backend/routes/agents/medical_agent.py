"""
Optimized LangChain ReAct Agent for Medical Chatbot
"""
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_community.chat_models import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from routes.agents.tools.medical_search_tool import get_medical_tools

load_dotenv()


# ==========================================
# 🤖 Optimized Medical Agent Class
# ==========================================
class MedicalAgent:
    """
    Optimized LangChain ReAct Agent with:
    - Pre-loaded components
    - Structured output format
    - Faster response time
    """
    
    def __init__(self, provider="ollama", model_name="qwen2.5:7b", temperature=0.4, 
                 ollama_url="http://localhost:11434"):
        """
        Initialize Medical Agent
        
        Args:
            provider: "ollama" or "google"
            model_name: Model name
            temperature: Generation temperature
            ollama_url: Ollama API endpoint
        """
        self.provider = provider
        self.temperature = temperature
        self.ollama_url = ollama_url
        
        # Select LLM
        if provider == "ollama":
            self.model_name = model_name or "qwen2.5:7b"
            
            # Test Ollama connection
            import requests
            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    raise Exception(f"Ollama returned status {response.status_code}")
                print(f"✅ Ollama connected at {ollama_url}")
            except Exception as e:
                print(f"❌ Cannot connect to Ollama: {e}")
                print("   Make sure Ollama is running: ollama serve")
                raise ValueError("Ollama connection failed!")
            
            self.llm = ChatOllama(
                model=self.model_name,
                base_url=ollama_url,
                temperature=temperature,
                num_predict=2048,  # ✅ GIẢM từ 4096 → 2048 để nhanh hơn
            )
        else:  # google
            self.model_name = model_name or "gemini-1.5-flash"
            self.llm = ChatGoogleGenerativeAI(
                api_key=os.getenv("GOOGLE_API_KEY"),
                model=self.model_name,
                temperature=temperature
            )
        
        # Get tools
        self.tools = get_medical_tools()
        
        # ==========================================
        # ✅ IMPROVED SYSTEM PROMPT với Output Format
        # ==========================================
        system_prompt = """Bạn là trợ lý y tế AI thông minh và chuyên nghiệp.

🎯 NHIỆM VỤ:
1. Phân tích câu hỏi người dùng
2. Quyết định có cần sử dụng tool `search_medical_documents` hay không
3. Trả lời theo format chuẩn dưới đây

📋 LUẬT SỬ DỤNG TOOL:
- Câu hỏi y tế (triệu chứng, bệnh, thuốc) → SỬ DỤNG tool
- Chào hỏi đơn giản (xin chào, hi) → KHÔNG dùng tool
- Cảm ơn, tạm biệt → KHÔNG dùng tool

📝 FORMAT TRẢ LỜI CỦA BẠN (khi có thông tin y tế):

**🔍 PHÂN TÍCH TRIỆU CHỨNG**
[Tóm tắt ngắn gọn triệu chứng người dùng mô tả]

**🏥 CÁC BỆNH/TÌNH TRẠNG CÓ THỂ LIÊN QUAN**

1. **[Tên bệnh 1]**
   - Giải thích: [Tại sao bệnh này liên quan đến triệu chứng]
   - Triệu chứng điển hình: [Các triệu chứng chính]
   - Mức độ nghiêm trọng: [Nhẹ/Trung bình/Nặng]

2. **[Tên bệnh 2]**
   - Giải thích: [...]
   - Triệu chứng điển hình: [...]
   - Mức độ nghiêm trọng: [...]

**⚠️ DẤU HIỆU CẦN ĐI KHÁM NGAY**
- [Dấu hiệu nguy hiểm 1]
- [Dấu hiệu nguy hiểm 2]
- [Dấu hiệu nguy hiểm 3]

**💡 KHUYẾN NGHỊ**
- Theo dõi: [Hướng dẫn theo dõi triệu chứng]
- Tự chăm sóc: [Các biện pháp tự chăm sóc tại nhà]
- Khi nào cần gặp bác sĩ: [Tình huống cần đi khám]

**⚕️ LƯU Ý QUAN TRỌNG**
Đây chỉ là thông tin tham khảo, KHÔNG phải chẩn đoán y khoa. Hãy gặp bác sĩ để được khám và chẩn đoán chính xác.

---

VÍ DỤ TRẢ LỜI TỐT:

Người dùng: "Tôi bị đau đầu và sốt"

**🔍 PHÂN TÍCH TRIỆU CHỨNG**
Bạn đang có triệu chứng đau đầu kèm sốt, đây là dấu hiệu phổ biến của nhiều tình trạng nhiễm trúng hoặc viêm nhiễm.

**🏥 CÁC BỆNH/TÌNH TRẠNG CÓ THỂ LIÊN QUAN**

1. **Cảm cúm thông thường**
   - Giải thích: Virus cảm cúm thường gây sốt 38-39°C kèm đau đầu, đau người
   - Triệu chứng điển hình: Sốt, đau đầu, nghẹt mũi, ho, mệt mỏi
   - Mức độ nghiêm trọng: Nhẹ đến trung bình

2. **Viêm xoang**
   - Giải thích: Viêm xoang gây áp lực ở vùng mặt, dẫn đến đau đầu và có thể sốt nhẹ
   - Triệu chứng điển hình: Đau đầu vùng trán/má, nghẹt mũi, sốt nhẹ
   - Mức độ nghiêm trọng: Trung bình

**⚠️ DẤU HIỆU CẦN ĐI KHÁM NGAY**
- Sốt trên 39.5°C kéo dài quá 3 ngày
- Đau đầu dữ dội, đột ngột
- Cứng gáy, lú lẫn, hoặc co giật
- Nôn mửa liên tục

**💡 KHUYẾN NGHỊ**
- Theo dõi: Đo nhiệt độ mỗi 4 giờ, ghi chép triệu chứng
- Tự chăm sóc: Nghỉ ngơi đầy đủ, uống nhiều nước, dùng thuốc hạ sốt (paracetamol)
- Khi nào cần gặp bác sĩ: Nếu sốt không hạ sau 3 ngày hoặc có dấu hiệu nặng

**⚕️ LƯU Ý QUAN TRỌNG**
Đây chỉ là thông tin tham khảo, KHÔNG phải chẩn đoán y khoa. Hãy gặp bác sĩ để được khám và chẩn đoán chính xác.

---

QUAN TRỌNG:
- HÃY tuân thủ CHÍNH XÁC format trên
- Không được tự ý thay đổi cấu trúc
- Luôn sử dụng emoji và markdown cho dễ đọc"""
        
        # Create agent
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,  # ✅ GIẢM từ 8 → 5
            max_execution_time=60,  # ✅ GIẢM từ 120 → 60 giây
            agent_kwargs={
                "prefix": system_prompt
            },
            early_stopping_method="generate"
        )
        
        print(f"✅ Medical Agent initialized")
        print(f"   Provider: {provider}")
        print(f"   Model: {self.model_name}")
        print(f"   Tools: {len(self.tools)}")
    
    def chat(self, query: str, chat_history: list = None) -> dict:
        """
        Chat với agent
        
        Args:
            query: User question
            chat_history: Previous conversation
        
        Returns:
            dict: {'answer': str, 'used_tools': bool, 'intermediate_steps': list}
        """
        try:
            print(f"\n{'='*60}")
            print(f"🤖 AGENT PROCESSING")
            print(f"{'='*60}")
            print(f"Query: {query[:50]}...")
            
            # ✅ GIỚI HẠN HISTORY để giảm context
            history_str = ""
            if chat_history:
                for msg in chat_history[-5:]:  # ✅ Chỉ lấy 5 tin nhắn gần nhất
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    history_str += f"{role}: {msg['content'][:100]}...\n"  # ✅ Cắt ngắn nội dung
            
            # Add history to query if exists
            full_input = query
            if history_str:
                full_input = f"Lịch sử:\n{history_str}\n\nCâu hỏi: {query}"
            
            # Run agent
            result = self.agent_executor.invoke({"input": full_input})
            
            # Parse result
            answer = result.get('output', 'Xin lỗi, tôi không thể trả lời câu hỏi này.')
            intermediate_steps = result.get('intermediate_steps', [])
            
            # Check if tools were used
            used_tools = len(intermediate_steps) > 0
            
            print(f"\n✅ COMPLETED ({len(intermediate_steps)} steps)")
            print(f"{'='*60}\n")
            
            return {
                'answer': answer,
                'used_tools': used_tools,
                'intermediate_steps': intermediate_steps
            }
            
        except Exception as e:
            print(f"❌ Error in agent: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'answer': "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                'used_tools': False,
                'intermediate_steps': []
            }


# ==========================================
# 🎯 Singleton Instance
# ==========================================
_agent_instance = None

def get_medical_agent(provider="ollama", model_name=None):
    """Get or create agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MedicalAgent(
            provider=provider,
            model_name=model_name
        )
    return _agent_instance


# ==========================================
# 🔌 Wrapper for Flask Controller
# ==========================================
def chat_with_agent(messages: list) -> str:
    """
    Wrapper function for Flask chat_controller
    
    Args:
        messages: Conversation history
    
    Returns:
        str: Agent's response
    """
    try:
        # Get agent (sử dụng singleton đã pre-load)
        agent = get_medical_agent(provider="ollama", model_name="qwen2.5:7b")
        
        # Extract last message
        last_message = messages[-1]['content'] if messages else ""
        
        # Chat with agent
        result = agent.chat(
            query=last_message,
            chat_history=messages[:-1]  # Exclude last message
        )
        
        # Log tool usage
        if result['used_tools']:
            print(f"💡 Agent used tools to answer")
        else:
            print(f"💡 Agent answered directly (no tools)")
        
        return result['answer']
        
    except Exception as e:
        print(f"❌ Error in chat_with_agent: {e}")
        import traceback
        traceback.print_exc()
        return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."