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

    def __init__(self, model_name="models/gemini-2.5-flash", temperature=0.3):
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

        # System prompt - natural and flexible
        self.system_prompt = """Bạn là VieMedChat - trợ lý y tế AI thân thiện, chuyên nghiệp.

🎯 NHIỆM VỤ:
Phân tích câu hỏi và LUÔN gọi một trong các công cụ bên dưới.

🛠️ CÁC CÔNG CỤ:
1. **search_medical_documents** - Tìm thông tin y tế (triệu chứng, bệnh, thuốc, điều trị)
2. **calculator** - Tính toán (BMI, công thức)
3. **general_chat** - Trò chuyện thông thường

📋 CÁCH PHÂN LOẠI:

A. Gọi search_medical_documents khi hỏi về:
   - Triệu chứng: đau đầu, sốt, ho, đau bụng
   - Bệnh: tiểu đường, cao huyết áp
   - Thuốc, cách điều trị, phòng ngừa

B. Gọi calculator khi có phép tính, công thức

C. Gọi general_chat khi:
   - Chào hỏi, cảm ơn, tạm biệt
   - Câu hỏi không liên quan y tế

💬 CÁCH TRẢ LỜI (SAU KHI CÓ KẾT QUẢ TỪ TOOL):

Trả lời tự nhiên, thân thiện như đang trò chuyện với bạn bè. KHÔNG dùng format cứng nhắc như "Bước 1", "Bước 2".

Ví dụ cách trả lời tốt:
"Chào bạn! Về tình trạng đau bụng của bạn, có thể do nhiều nguyên nhân như... Bạn có thể thử chườm nóng để giảm đau. Nếu đau nhiều hoặc kéo dài, nên đi khám bác sĩ nhé!"

Nguyên tắc:
- Thân thiện, gần gũi, có emoji phù hợp 😊
- Dùng ngôn ngữ tự nhiên, dễ hiểu
- Tổng hợp thông tin từ tool một cách mạch lạc
- Đưa ra lời khuyên thực tế
- Luôn nhắc đi khám bác sĩ nếu nghiêm trọng
- KHÔNG liệt kê theo format cứng nhắc
- Trả lời bằng TIẾNG VIỆT CÓ DẤU

⚠️ QUY TẮC BẮT BUỘC:
- PHẢI gọi tool trước khi trả lời
- Nếu không chắc loại câu hỏi → gọi general_chat"""

        print(f"Tool Calling Agent initialized (Direct binding)")
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
            print(f"TOOL CALLING AGENT (Direct)")
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
            tool_calls = []
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_calls = response.tool_calls
                print(f"LLM requested {len(tool_calls)} tool call(s)")
            else:
                # FORCE general_chat if no tool is called
                print("LLM did not call any tool. Forcing general_chat...")
                tool_calls = [{"name": "general_chat", "args": {"query": query}}]

            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})

                print(f"   -> Calling {tool_name} with args: {tool_args}")

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
                    answer = f"Loi: Tool '{tool_name}' khong ton tai."

            print(f"\nCOMPLETED")
            print(f"   Tools used: {len(tool_calls_made)}")
            print(f"{'='*60}\n")

            return {
                "answer": answer,
                "used_tools": len(tool_calls_made) > 0,
                "tool_calls": tool_calls_made,
                "api_calls": len(tool_calls_made) + 1,
            }

        except Exception as e:
            print(f"Error in agent: {e}")
            import traceback

            traceback.print_exc()

            return {
                "answer": "Xin loi, toi dang gap su co ky thuat. Vui long thu lai sau.",
                "used_tools": False,
                "tool_calls": [],
                "api_calls": 0,
            }


# ==========================================
# Singleton Instance
# ==========================================
_agent_instance = None


def get_medical_agent_tool_calling(model_name="models/gemini-2.5-flash"):
    """Get or create tool calling agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        try:
            _agent_instance = MedicalAgentToolCalling(model_name=model_name)
        except Exception as e:
            print(f"Failed to create agent instance: {e}")
            _agent_instance = None
            raise
    return _agent_instance


# ==========================================
# Wrapper for Flask Controller
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
        agent = get_medical_agent_tool_calling(model_name="models/gemini-2.5-flash")

        # Extract last message
        last_message = messages[-1]["content"] if messages else ""

        # Chat with agent
        result = agent.chat(query=last_message, chat_history=messages[:-1])

        print(f"Tool Calling: {result['api_calls']} API calls")

        return result["answer"]

    except Exception as e:
        print(f"Error in chat_with_agent: {e}")
        import traceback

        traceback.print_exc()
        return "Xin loi, toi dang gap su co ky thuat. Vui long thu lai sau."
