# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# import ollama

# try:
#     from rag.prompt import *
# except ImportError:
#     from prompt import *

# load_dotenv(".env")


# class LLM:
#     def __init__(self, google_api_key=None,
#                  temperature=0.4, model_name=None, ollama_use=False, language="vi"):
#         """
#         Wrapper cho nhiều backend LLM (Google, Ollama).
#         :param google_api_key: key cho Google Generative AI
#         :param temperature: độ ngẫu nhiên
#         :param model_name: tên model (nếu Ollama)
#         :param ollama_use: True nếu dùng Ollama
#         :param language: 'vi' hoặc 'en'
#         """
#         self.google_api_key = google_api_key
#         self.temperature = temperature
#         self.model_name = model_name
#         self.ollama_use = ollama_use
#         self.language = language.lower()

#         # Init backend
#         if self.ollama_use:
#             self.llm = None  # Ollama gọi riêng
#         elif model_name == "google" and google_api_key:
#             self.llm = ChatGoogleGenerativeAI(
#                 model="gemini-2.0-flash",  # ✅ model mới free tier
#                 google_api_key=google_api_key,
#                 temperature=temperature,
#                 max_output_tokens=4096,
#             )
#         else:
#             raise ValueError("❌ Cấu hình LLM không hợp lệ. Vui lòng kiểm tra API key và model_name.")

#     def preprocess_prompt(self, question: str, context: str = None) -> str:
#         """Tạo prompt dựa vào language và có/không có context."""
#         if self.language == "en":
#             if context:
#                 user_message = USER_MESSAGE_WITH_CONTEXT_EN.format(context=context, question=question)
#                 prompt = DEFAULT_PROMPT_EN.format(user_message=user_message)
#             else:
#                 prompt = DEFAULT_PROMPT_EN.format(user_message=question)
#         else:  # default VN
#             if context:
#                 user_message = USER_MESSAGE_WITH_CONTEXT_VN.format(context=context, question=question)
#                 prompt = DEFAULT_PROMPT_VN.format(user_message=user_message)
#             else:
#                 prompt = DEFAULT_PROMPT_VN.format(user_message=question)
#         return prompt

#     def generate(self, prompt: str) -> str:
#         """Sinh output từ backend đã chọn."""
#         if self.ollama_use:
#             return ollama.generate(model=self.model_name, prompt=prompt)["response"]

#         if self.google_api_key:
#             return self.llm.invoke(prompt).content

#         raise RuntimeError("❌ Không có backend nào khả dụng để generate.")


# # if __name__ == "__main__":
# #     google_api_key = os.getenv("GOOGLE_API_KEY")

# #     # Ví dụ: Chatbot y tế bằng Google Gemini
# #     llm = LLM(google_api_key=google_api_key, model_name="google", language="vi")

# #     question = "Việc sử dụng thuốc kháng sinh một cách tự tiện, quá liều lượng, không theo đơn có thể gây ra vấn đề nào?"
# #     prompt = llm.preprocess_prompt(question=question)
# #     result = llm.generate(prompt)
# #     print(result)


import os
from dotenv import load_dotenv
import google.generativeai as genai

try:
    from prompt import *
except ImportError:
    from .prompt import *

load_dotenv(".env")


class LLM:
    """
    Simple LLM wrapper using direct Google Generative AI API
    No LangChain dependencies
    """
    
    def __init__(self, google_api_key=None, temperature=0.4, 
                 model_name="gemini-2.0-flash-exp", language="vi"):
        """
        Initialize LLM
        
        Args:
            google_api_key: Google API key
            temperature: Temperature for generation (0-1)
            model_name: Gemini model name
            language: 'vi' or 'en'
        """
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.temperature = temperature
        self.model_name = model_name
        self.language = language.lower()
        
        if not self.google_api_key:
            raise ValueError("❌ GOOGLE_API_KEY is required!")
        
        # Configure Gemini
        genai.configure(api_key=self.google_api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=4096,
            )
        )
        
        print(f"✅ LLM initialized: {self.model_name}")
        print(f"   Language: {self.language}")
        print(f"   Temperature: {self.temperature}")

    def preprocess_prompt(self, question: str, context: str = None) -> str:
        """Tạo prompt dựa vào language và có/không có context."""
        if self.language == "en":
            if context:
                user_message = USER_MESSAGE_WITH_CONTEXT_EN.format(context=context, question=question)
                prompt = DEFAULT_PROMPT_EN.format(user_message=user_message)
            else:
                prompt = DEFAULT_PROMPT_EN.format(user_message=question)
        else:  # default VN
            if context:
                user_message = USER_MESSAGE_WITH_CONTEXT_VN.format(context=context, question=question)
                prompt = DEFAULT_PROMPT_VN.format(user_message=user_message)
            else:
                prompt = DEFAULT_PROMPT_VN.format(user_message=question)
        return prompt

    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."
    
    def chat(self, question: str, context: str = None) -> str:
        """
        Convenience method for chat
        
        Args:
            question: User question
            context: Optional context
        
        Returns:
            Generated answer
        """
        prompt = self.preprocess_prompt(question, context)
        return self.generate(prompt)

