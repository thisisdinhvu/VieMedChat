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
    
    def __init__(self, provider="google", model_name="models/gemini-2.0-flash-lite", temperature=0.4, 
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
            self.model_name = model_name or "models/gemini-2.0-flash-lite"
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

🛠️ BẠN CÓ 3 CÔNG CỤ:
1. **search_medical_documents** - Tìm kiếm thông tin y tế
2. **calculator** - Tính toán số học
3. **general_chat** - Trò chuyện thông thường

🎯 CÁCH CHỌN TOOL ĐÚNG:

**1. Câu hỏi Y TẾ** → `search_medical_documents`
   - Triệu chứng: "đau đầu", "sốt", "buồn nôn"
   - Bệnh: "tiểu đường", "cao huyết áp", "viêm gan"
   - Thuốc: "paracetamol", "aspirin"
   - Điều trị: "cách chữa", "nên làm gì"

**2. Câu hỏi TÍNH TOÁN** → `calculator`
   - "2 + 2 bằng bao nhiêu?"
   - "Tính 15% của 200"
   - "100 chia 4"
   - Bất kỳ phép toán nào

**3. Câu hỏi CHUNG CHUNG** → `general_chat`
   - Chào hỏi: "xin chào", "hi", "hello"
   - Hỏi về bot: "bạn là ai?", "bạn tên gì?"
   - Cảm ơn: "cảm ơn", "thanks"
   - Tạm biệt: "bye", "tạm biệt"
   - Trò chuyện thông thường

📝 FORMAT TRẢ LỜI (khi có thông tin y tế từ tool):

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

**💡 KHUYẾN NGHỊ**
- Theo dõi: [Hướng dẫn theo dõi]
- Tự chăm sóc: [Biện pháp tại nhà]
- Khi nào cần gặp bác sĩ: [Tình huống]

**⚕️ LƯU Ý QUAN TRỌNG**
Đây chỉ là thông tin tham khảo, KHÔNG phải chẩn đoán y khoa. Hãy gặp bác sĩ để được khám chính xác.

---

VÍ DỤ SỬ DỤNG TOOLS:

**VD 1: Y tế**
User: "Tôi bị đau đầu và sốt"
→ Dùng: search_medical_documents("đau đầu và sốt")
→ Trả lời theo format y tế ở trên

**VD 2: Tính toán**
User: "2 + 2 bằng bao nhiêu?"
→ Dùng: calculator("2 + 2")
→ Trả lời: "Kết quả: 2 + 2 = 4"

**VD 3: Chào hỏi**
User: "xin chào"
→ Dùng: general_chat("xin chào")
→ Trả lời: [Câu trả lời thân thiện từ tool]

QUAN TRỌNG:
- Luôn chọn tool PHÙ HỢP nhất
- Không dùng search_medical_documents cho câu chào hỏi
- Không dùng calculator cho câu hỏi y tế
- Trả lời bằng TIẾNG VIỆT, không được trả lời bằng ngôn ngữ khác như TIẾNG ANH, PHÁP, TRUNG"""
        
        # Create agent
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,  # ✅ GIẢM từ 8 → 5
            max_execution_time=60,  # ✅ GIẢM từ 120 → 60 giây
            agent_kwargs={
                "prefix": system_prompt,
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

def get_medical_agent(provider="google", model_name=None):
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
        agent = get_medical_agent(provider="google", model_name="models/gemini-2.0-flash-lite")
        
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