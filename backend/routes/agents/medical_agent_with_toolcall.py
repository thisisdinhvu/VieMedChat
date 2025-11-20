"""
Optimized Medical Agent using Tool Calling (Function Calling)
Direct implementation using llm.bind_tools() - bypasses LangChain agent framework
More efficient than ReAct - saves 50-70% API quota!
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from routes.agents.tools.medical_search_tool import get_medical_tools

load_dotenv()


class MedicalAgentToolCalling:
    """
    Optimized Medical Agent using Direct Tool Calling
    Bypasses LangChain agent framework to avoid compatibility issues

    Benefits:
    - 50-70% fewer API calls vs ReAct
    - Faster response (1-2 calls vs 3-5 calls)
    - Lower token usage (no verbose thinking)
    - Better accuracy (structured outputs)
    """

    def __init__(self, model_name="models/gemini-2.0-flash-lite", temperature=0.3):
        """
        Initialize Tool Calling Agent using direct llm.bind_tools()

        Args:
            model_name: Gemini model (must support function calling)
            temperature: Generation temperature
        """
        self.model_name = model_name
        self.temperature = temperature

        # Initialize LLM with function calling support
        self.llm = ChatGoogleGenerativeAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=self.model_name,
            temperature=temperature,
            max_retries=2,
        )

        # Get tools
        self.tools = get_medical_tools()

        # Create tool map for execution
        self.tool_map = {tool.name: tool.func for tool in self.tools}

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # System prompt with Chain-of-Thought reasoning
        self.system_prompt = """Bạn là trợ lý y tế AI chuyên nghiệp.

🎯 NHIỆM VỤ:
Phân tích câu hỏi và LUÔN LUÔN gọi một trong các công cụ bên dưới.

🛠️ CÁC CÔNG CỤ:
1. **search_medical_documents** - Tìm kiếm thông tin y tế (triệu chứng, bệnh, thuốc, điều trị)
2. **calculator** - Tính toán số học, công thức toán học
3. **general_chat** - Trò chuyện thông thường, câu hỏi không liên quan y tế hoặc toán học

⚡ QUY TRÌNH (BẮT BUỘC):
1. Đọc câu hỏi của người dùng
2. Phân loại câu hỏi thuộc loại nào
3. GỌI TOOL TƯƠNG ỨNG (KHÔNG BAO GIỜ BỎ QUA BƯỚC NÀY)
4. Nhận kết quả từ tool
5. Áp dụng Chain-of-Thought để trả lời

🧠 CHAIN-OF-THOUGHT REASONING (Chỉ áp dụng cho câu hỏi y tế):

Khi trả lời câu hỏi y tế, hãy suy nghĩ và trình bày theo cấu trúc:

**📋 Bước 1: Phân tích triệu chứng**
- Liệt kê các triệu chứng/vấn đề user đề cập
- Đánh giá mức độ: nhẹ/trung bình/nghiêm trọng

**🔍 Bước 2: Tìm kiếm & So sánh**
- Dựa trên thông tin từ tool
- So sánh triệu chứng với các bệnh/tình trạng có thể

**💡 Bước 3: Kết luận & Khuyến nghị**
- Đưa ra kết luận dựa trên phân tích
- Khuyến nghị cụ thể (đi khám, tự chăm sóc, v.v.)
- Lưu ý: Luôn khuyên đi khám bác sĩ nếu nghiêm trọng

📌 QUY TẮC QUAN TRỌNG (BẮT BUỘC TUÂN THỦ):
❗ BẠN PHẢI LUÔN GỌI MỘT TOOL - TUYỆT ĐỐI KHÔNG TRẢ LỜI TRỰC TIẾP
❗ Nếu không chắc chắn, hãy gọi general_chat
❗ SAU KHI tool trả kết quả, áp dụng Chain-of-Thought để trả lời
❗ Trả lời bằng TIẾNG VIỆT, RÕ RÀNG, LOGIC, DỄ HIỂU

🔍 HƯỚNG DẪN PHÂN LOẠI:

A. Gọi search_medical_documents khi:
   - Hỏi về triệu chứng: "đau đầu", "sốt", "ho", "đau bụng"
   - Hỏi về bệnh: "tiểu đường", "cao huyết áp", "ung thư"
   - Hỏi về thuốc: "paracetamol", "kháng sinh"
   - Hỏi về điều trị: "cách chữa", "phòng ngừa"
   - Hỏi về sức khỏe: "dinh dưỡng", "tập thể dục"

B. Gọi calculator khi:
   - Có phép tính: "2+2", "căn bậc 3 của 27"
   - Có công thức: "BMI", "diện tích"
   - Có số học: "tính", "bằng bao nhiêu"

C. Gọi general_chat khi:
   - Chào hỏi: "xin chào", "hello", "chào bạn"
   - Cảm ơn: "cảm ơn", "thanks"
   - Hỏi thời tiết: "thời tiết", "trời"
   - Hỏi thông tin chung: "món ăn", "du lịch", "giải trí"
   - Trò chuyện: "bạn là ai", "bạn làm gì"
   - BẤT KỲ CÂU HỎI NÀO KHÔNG THUỘC Y TẾ HOẶC TOÁN HỌC

📚 VÍ DỤ CỤ THỂ:

1. "xin chào" 
   → BẮT BUỘC gọi: general_chat("xin chào")
   
2. "thời tiết hôm nay thế nào?"
   → BẮT BUỘC gọi: general_chat("thời tiết hôm nay thế nào?")
   
3. "tôi thèm ăn cơm gà"
   → BẮT BUỘC gọi: general_chat("tôi thèm ăn cơm gà")
   
4. "2+2 bằng bao nhiêu?"
   → BẮT BUỘC gọi: calculator("2+2")
   
5. "căn bậc 3 của 27"
   → BẮT BUỘC gọi: calculator("27**(1/3)")
   
6. "Tôi bị đau đầu"
   → BẮT BUỘC gọi: search_medical_documents("đau đầu")
   → Trả lời theo Chain-of-Thought:
     📋 Triệu chứng: Đau đầu
     🔍 Phân tích: [Dựa trên kết quả tool]
     💡 Kết luận: [Khuyến nghị cụ thể]
   
7. "Paracetamol dùng như thế nào?"
   → BẮT BUỘC gọi: search_medical_documents("paracetamol")

⚠️ LƯU Ý:
- Nếu không chắc chắn câu hỏi thuộc loại nào → Gọi general_chat
- KHÔNG BAO GIỜ trả lời trực tiếp mà không gọi tool
- Luôn gọi tool TRƯỚC KHI trả lời
- Với câu hỏi y tế, luôn áp dụng Chain-of-Thought để trả lời có cấu trúc"""

        print(f"✅ Tool Calling Agent initialized (Direct binding)")
        print(f"   Model: {self.model_name}")
        print(f"   Tools: {len(self.tools)}")

    def chat(self, query: str, chat_history: list = None) -> dict:
        """
        Chat with agent using tool calling

        Args:
            query: User question
            chat_history: Previous conversation (ignored for now)

        Returns:
            dict: {
                'answer': str,
                'used_tools': bool,
                'tool_calls': list
            }
        """
        try:
            print(f"\n{'='*60}")
            print(f"🤖 TOOL CALLING AGENT (Direct)")
            print(f"{'='*60}")
            print(f"Query: {query[:50]}...")

            # Prepare messages
            messages = [SystemMessage(content=self.system_prompt)]

            # Add chat history if available
            if chat_history:
                for msg in chat_history[
                    -10:
                ]:  # Limit to last 10 messages to save context
                    role = msg.get("role")
                    content = msg.get("content")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant" or role == "bot":
                        messages.append(AIMessage(content=content))

            # Add current query
            messages.append(HumanMessage(content=query))

            # First call - LLM decides which tool to use
            response = self.llm_with_tools.invoke(messages)

            tool_calls_made = []

            # Check if LLM wants to use tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                print(f"🔧 LLM requested {len(response.tool_calls)} tool call(s)")

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})

                    print(f"   → Calling {tool_name} with args: {tool_args}")

                    if tool_name in self.tool_map:
                        # Execute tool - handle both named args and positional args
                        try:
                            # Try with original args first
                            tool_result = self.tool_map[tool_name](**tool_args)
                        except TypeError as e:
                            # If that fails, try extracting positional args (__arg1, __arg2, etc.)
                            if "__arg1" in tool_args:
                                positional_args = []
                                i = 1
                                while f"__arg{i}" in tool_args:
                                    positional_args.append(tool_args[f"__arg{i}"])
                                    i += 1
                                tool_result = self.tool_map[tool_name](*positional_args)
                            else:
                                raise e

                        tool_calls_made.append(
                            {
                                "tool": tool_name,
                                "input": str(tool_args),
                                "output": str(tool_result)[:100],
                            }
                        )

                        # Add tool result to messages and get final answer
                        messages.append(response)
                        messages.append(
                            HumanMessage(
                                content=f"Tool result: {tool_result}\n\nBased on this, please provide your final answer to the user."
                            )
                        )

                        # Second call - LLM generates final answer
                        final_response = self.llm.invoke(messages)
                        answer = final_response.content
                    else:
                        answer = f"Lỗi: Tool '{tool_name}' không tồn tại."
            else:
                # No tool needed, use LLM response directly
                answer = response.content

            print(f"\n✅ COMPLETED")
            print(f"   Tools used: {len(tool_calls_made)}")
            print(f"{'='*60}\n")

            return {
                "answer": answer,
                "used_tools": len(tool_calls_made) > 0,
                "tool_calls": tool_calls_made,
                "api_calls": len(tool_calls_made) + 1,
            }

        except Exception as e:
            print(f"❌ Error in agent: {e}")
            import traceback

            traceback.print_exc()

            return {
                "answer": "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
                "used_tools": False,
                "tool_calls": [],
                "api_calls": 0,
            }


# ==========================================
# 🎯 Singleton Instance
# ==========================================
_agent_instance = None


def get_medical_agent_tool_calling(model_name="models/gemini-2.0-flash-lite"):
    """Get or create tool calling agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        try:
            _agent_instance = MedicalAgentToolCalling(model_name=model_name)
        except Exception as e:
            print(f"❌ Failed to create agent instance: {e}")
            _agent_instance = None
            raise
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
        agent = get_medical_agent_tool_calling(
            model_name="models/gemini-2.0-flash-lite"
        )

        # Extract last message
        last_message = messages[-1]["content"] if messages else ""

        # Chat with agent
        result = agent.chat(query=last_message, chat_history=messages[:-1])

        print(f"💡 Tool Calling: {result['api_calls']} API calls")

        return result["answer"]

    except Exception as e:
        print(f"❌ Error in chat_with_agent: {e}")
        import traceback

        traceback.print_exc()
        return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."
