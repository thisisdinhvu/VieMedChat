"""
LangChain ReAct Agent for Medical Chatbot
Agent tự động quyết định khi nào cần search documents
"""
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from routes.agents.tools.medical_search_tool import get_medical_tools

load_dotenv()


# ==========================================
# 🤖 Medical Agent Class
# ==========================================
class MedicalAgent:
    """
    LangChain ReAct Agent for medical chatbot
    Automatically decides when to use tools
    """
    
    def __init__(self, provider="groq", model_name=None, temperature=0.4):
        """
        Initialize Medical Agent
        
        Args:
            provider: "groq" or "google"
            model_name: Model name (auto-select if None)
            temperature: Generation temperature
        """
        self.provider = provider
        self.temperature = temperature
        
        # Select LLM
        if provider == "groq":
            self.model_name = model_name or "llama-3.3-70b-versatile"
            self.llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model=self.model_name,
                temperature=temperature
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
        
        # System prompt for agent
        system_prompt = """Bạn là trợ lý y tế AI thông minh và tận tâm.

Hướng dẫn:
1. **Phân tích câu hỏi**: Hiểu rõ người dùng đang hỏi gì
2. **Quyết định hành động**:
   - Nếu là chào hỏi đơn giản (xin chào, hi, hello): Trả lời trực tiếp KHÔNG dùng tool
   - Nếu là câu hỏi y tế (triệu chứng, bệnh, thuốc): SỬ DỤNG tool `search_medical_documents`
   - Nếu là cảm ơn/tạm biệt: Trả lời lịch sự KHÔNG dùng tool

3. **Trả lời câu hỏi y tế** (KHI ĐÃ CÓ THÔNG TIN TỪ TOOL):
   a) Liệt kê các bệnh/tình trạng có thể liên quan dựa trên context
   b) Giải thích ngắn gọn TẠI SAO các bệnh đó liên quan (dựa trên triệu chứng trong context)
   c) Nêu các triệu chứng cụ thể cần chú ý (từ context)
   d) Đưa ra khuyến nghị: khi nào cần đi khám gấp, cách theo dõi
   e) Nhắc nhở KHÔNG tự chẩn đoán, cần gặp bác sĩ

**QUAN TRỌNG**:
- LUÔN sử dụng tool cho câu hỏi y tế
- SAU KHI nhận Observation từ tool, HÃY phân tích CHI TIẾT từng tài liệu
- Câu trả lời PHẢI có CẤU TRÚC rõ ràng với các phần: Bệnh liên quan, Giải thích, Triệu chứng cần chú ý, Khuyến nghị
- Trả lời bằng tiếng Việt, dễ hiểu, có cấu trúc
- KHÔNG chẩn đoán dứt khoát, luôn khuyên gặp bác sĩ

**Ví dụ câu trả lời tốt**:
"Dựa trên triệu chứng đau đầu và sốt, có một số tình trạng có thể liên quan:

🔸 **Sốt rét**: Thông tin y tế cho thấy sốt rét thường có triệu chứng sốt cao (40-41°C) kèm đau đầu, rét run toàn thân...

🔸 **Viêm xoang**: Có thể gây đau đầu sau hốc mắt kèm sốt...

⚠️ **Dấu hiệu cần đi khám ngay**: Nếu sốt cao trên 39°C kéo dài, đau đầu dữ dội...

💡 **Khuyến nghị**: Theo dõi thân nhiệt, nghỉ ngơi... và nên đến cơ sở y tế để bác sĩ khám và chẩn đoán chính xác."

PHẢI trả lời theo cấu trúc trên, không được nói chung chung!"""
        
        # Create agent using initialize_agent
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=8,  # ✅ Tăng từ 5 lên 8
            max_execution_time=60,  # ✅ Tăng từ 30s lên 60s
            agent_kwargs={
                "prefix": system_prompt
            },
            early_stopping_method="generate"  # ✅ Thêm để force generate answer
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
            dict: {
                'answer': str,
                'used_tools': bool,
                'intermediate_steps': list
            }
        """
        try:
            print(f"\n{'='*60}")
            print(f"🤖 AGENT PROCESSING QUERY")
            print(f"{'='*60}")
            print(f"Query: {query}")
            
            # Format chat history
            history_str = ""
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    history_str += f"{role}: {msg['content']}\n"
            
            # Add history to query if exists
            full_input = query
            if history_str:
                full_input = f"Lịch sử trò chuyện:\n{history_str}\n\nCâu hỏi mới: {query}"
            
            # Run agent
            result = self.agent_executor.invoke({"input": full_input})
            
            # Parse result
            answer = result.get('output', 'Xin lỗi, tôi không thể trả lời câu hỏi này.')
            intermediate_steps = result.get('intermediate_steps', [])
            
            # Check if tools were used
            used_tools = len(intermediate_steps) > 0
            
            print(f"\n{'='*60}")
            print(f"✅ AGENT COMPLETED")
            print(f"   Used tools: {used_tools}")
            print(f"   Steps: {len(intermediate_steps)}")
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

def get_medical_agent(provider="groq", model_name=None):
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
        # Get agent
        agent = get_medical_agent(provider="groq")
        
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


# ==========================================
# 🧪 Testing
# ==========================================
if __name__ == "__main__":
    print("\n🧪 TESTING MEDICAL AGENT\n")
    
    agent = MedicalAgent(provider="groq")
    
    test_queries = [
        "xin chào",
        "tôi bị đau đầu và sốt, có nguy hiểm không?",
        "cảm ơn bạn"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = agent.chat(query)
        
        print(f"\n💬 Answer:")
        print(result['answer'])
        print(f"\n🔧 Used tools: {result['used_tools']}")