"""
LangChain ReAct Agent for Medical Chatbot
Agent tự động quyết định khi nào cần search documents
"""
import os
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from routes.agents.tools.medical_search_tool import get_medical_tools

load_dotenv()


# ==========================================
# 🤖 Agent Prompt (ReAct Pattern)
# ==========================================
MEDICAL_AGENT_PROMPT = """Bạn là trợ lý y tế AI thông minh và tận tâm.

Bạn có quyền truy cập vào các công cụ sau:

{tools}

Hướng dẫn:
1. **Phân tích câu hỏi**: Hiểu rõ người dùng đang hỏi gì
2. **Quyết định hành động**:
   - Nếu là chào hỏi đơn giản (xin chào, hi): Trả lời trực tiếp
   - Nếu là câu hỏi y tế: SỬ DỤNG tool `search_medical_documents`
   - Nếu là cảm ơn/tạm biệt: Trả lời lịch sự
3. **Trả lời**: Dựa trên thông tin từ tool hoặc kiến thức của bạn

**QUAN TRỌNG**:
- LUÔN sử dụng tool cho câu hỏi y tế (triệu chứng, bệnh, thuốc)
- KHÔNG sử dụng tool cho chào hỏi, cảm ơn
- Trả lời bằng tiếng Việt, dễ hiểu, thân thiện
- KHÔNG chẩn đoán dứt khoát, luôn khuyên gặp bác sĩ

Sử dụng format sau:

Question: câu hỏi bạn phải trả lời
Thought: suy nghĩ về cần làm gì
Action: tên công cụ cần dùng (hoặc "không cần tool")
Action Input: đầu vào cho công cụ
Observation: kết quả từ công cụ
... (lặp lại Thought/Action/Observation nếu cần)
Thought: Tôi đã có đủ thông tin để trả lời
Final Answer: câu trả lời cuối cùng cho người dùng

Bắt đầu!

Previous conversation:
{chat_history}

New question: {input}
{agent_scratchpad}
"""


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
        
        # Create prompt
        self.prompt = PromptTemplate.from_template(MEDICAL_AGENT_PROMPT)
        
        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,  # Debug logging
            handle_parsing_errors=True,
            max_iterations=5,
            max_execution_time=30,
            return_intermediate_steps=True
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
            
            # Run agent
            result = self.agent_executor.invoke({
                "input": query,
                "chat_history": history_str
            })
            
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