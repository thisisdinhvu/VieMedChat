"""
Calculator Tool for LangChain Agent
Performs basic arithmetic operations
"""

from langchain.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional
import re


# ==========================================
# 📊 Input Schema
# ==========================================
class CalculatorInput(BaseModel):
    """Input schema for calculator"""

    expression: str = Field(
        description="Biểu thức toán học cần tính. "
        "Ví dụ: '2 + 2', '10 * 5', '100 / 4', '(3 + 5) * 2'"
    )


# ==========================================
# 🧮 Calculator Function
# ==========================================
def calculate(expression: str) -> str:
    """
    Calculate basic math expressions safely.

    Use this tool when:
    - User asks to calculate something
    - User provides a math expression
    - User needs numerical computation

    Supports: +, -, *, /, (), powers (**)

    Examples:
    - "2 + 2" → "4"
    - "10 * 5 + 3" → "53"
    - "(100 - 20) / 4" → "20.0"

    Args:
        expression: Math expression as string

    Returns:
        str: Calculation result or error message
    """
    try:
        print(f"\n🧮 CALCULATOR TOOL CALLED")
        print(f"   Expression: {expression}")

        # Clean expression (remove spaces, validate characters)
        expression = expression.strip()

        # Security: Only allow safe characters
        if not re.match(r"^[\d\s\+\-\*\/\(\)\.\*\*]+$", expression):
            return "❌ Lỗi: Biểu thức chứa ký tự không hợp lệ. Chỉ cho phép: +, -, *, /, (), số"

        # Evaluate safely
        result = eval(expression, {"__builtins__": {}})

        print(f"   ✅ Result: {result}")

        # Format result nicely
        if isinstance(result, float) and result.is_integer():
            return f"Kết quả: {int(result)}"
        else:
            return f"Kết quả: {result}"

    except ZeroDivisionError:
        return "❌ Lỗi: Không thể chia cho 0"

    except SyntaxError:
        return (
            "❌ Lỗi: Cú pháp biểu thức không đúng. Ví dụ đúng: '2 + 2', '10 * (5 - 3)'"
        )

    except Exception as e:
        print(f"   ❌ Calculator error: {e}")
        return f"❌ Lỗi khi tính toán: {str(e)}"


# ==========================================
# 🛠️ LangChain Tool Definition
# ==========================================
def get_calculator_tool():
    """
    Get calculator tool for LangChain agent

    Returns:
        Tool: LangChain Tool object
    """
    return Tool(
        name="calculator",
        func=calculate,
        description="""
            Công cụ tính toán số học cơ bản.
            
            SỬ DỤNG khi:
            - Người dùng yêu cầu tính toán
            - Cần thực hiện phép toán (+, -, *, /)
            - Câu hỏi chứa số và phép tính
            
            KHÔNG SỬ DỤNG khi:
            - Câu hỏi y tế
            - Câu hỏi chung (chào hỏi, cảm ơn)
            - Không có phép tính cụ thể
            
            Ví dụ sử dụng:
            - "2 + 2 bằng bao nhiêu?" → calculator("2 + 2")
            - "Tính 15% của 200" → calculator("200 * 0.15")
            - "100 chia 4" → calculator("100 / 4")
            
            Input: Biểu thức toán học (string)
            Output: Kết quả tính toán
        """,
        args_schema=CalculatorInput,  # Tạm comment để test
        return_direct=False,
    )
