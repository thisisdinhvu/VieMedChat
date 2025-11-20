# import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# from groq import Groq

# try:
#     from prompt import *
# except ImportError:
#     from .prompt import *

# load_dotenv(".env")


# class LLM:
#     """
#     LLM wrapper supporting:
#     - Google Gemini
#     - Groq (Llama, Mixtral, Gemma)
#     """

#     def __init__(self, google_api_key=None, groq_api_key=None,
#                  temperature=0.4, model_name="groq/llama-3.3-70b-versatile",
#                  language="vi"):
#         """
#         Initialize LLM

#         Args:
#             google_api_key: Google API key
#             groq_api_key: Groq API key
#             temperature: Temperature for generation (0-1)
#             model_name: Model name with provider prefix:
#                 - "models/gemini-2.0-flash" (Google)
#                 - "groq/llama-3.3-70b-versatile" (Groq - BEST FREE)
#                 - "groq/llama-3.1-8b-instant" (Groq - Fastest)
#                 - "groq/mixtral-8x7b-32768" (Groq - Long context)
#             language: 'vi' or 'en'
#         """
#         self.temperature = temperature
#         self.model_name = model_name
#         self.language = language.lower()

#         # Determine provider
#         if model_name.startswith("groq/"):
#             self.provider = "groq"
#             self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
#             if not self.groq_api_key:
#                 raise ValueError("❌ GROQ_API_KEY is required!")

#             self.client = Groq(api_key=self.groq_api_key)
#             self.model_id = model_name.replace("groq/", "")
#             print(f"✅ LLM initialized: Groq - {self.model_id}")

#         else:  # Default to Gemini
#             self.provider = "gemini"
#             self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
#             if not self.google_api_key:
#                 raise ValueError("❌ GOOGLE_API_KEY is required!")

#             genai.configure(api_key=self.google_api_key)
#             self.model = genai.GenerativeModel(
#                 model_name=self.model_name,
#                 generation_config=genai.GenerationConfig(
#                     temperature=self.temperature,
#                     max_output_tokens=4096,
#                 )
#             )
#             print(f"✅ LLM initialized: Gemini - {self.model_name}")

#         print(f"   Language: {self.language}")
#         print(f"   Temperature: {self.temperature}")

#     def preprocess_prompt(self, question: str, context: str = None) -> str:
#         """Create prompt based on language and context"""
#         if self.language == "en":
#             if context:
#                 user_message = USER_MESSAGE_WITH_CONTEXT_EN.format(
#                     context=context, question=question
#                 )
#                 prompt = DEFAULT_PROMPT_EN.format(user_message=user_message)
#             else:
#                 prompt = DEFAULT_PROMPT_EN.format(user_message=question)
#         else:  # Vietnamese
#             if context:
#                 user_message = USER_MESSAGE_WITH_CONTEXT_VN.format(
#                     context=context, question=question
#                 )
#                 prompt = DEFAULT_PROMPT_VN.format(user_message=user_message)
#             else:
#                 prompt = DEFAULT_PROMPT_VN.format(user_message=question)
#         return prompt

#     def generate(self, prompt: str) -> str:
#         """
#         Generate response from LLM

#         Args:
#             prompt: Input prompt

#         Returns:
#             Generated text
#         """
#         try:
#             if self.provider == "groq":
#                 # Groq API
#                 response = self.client.chat.completions.create(
#                     model=self.model_id,
#                     messages=[
#                         {"role": "user", "content": prompt}
#                     ],
#                     temperature=self.temperature,
#                     max_tokens=4096,
#                 )
#                 return response.choices[0].message.content

#             else:  # Gemini
#                 response = self.model.generate_content(prompt)
#                 return response.text

#         except Exception as e:
#             error_msg = str(e)
#             print(f"❌ Error generating response: {error_msg}")

#             # Handle rate limits
#             if "429" in error_msg or "quota" in error_msg.lower():
#                 return "Xin lỗi, hệ thống đang quá tải. Vui lòng thử lại sau 1 phút."

#             return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."

#     def chat(self, question: str, context: str = None) -> str:
#         """
#         Convenience method for chat

#         Args:
#             question: User question
#             context: Optional context

#         Returns:
#             Generated answer
#         """
#         prompt = self.preprocess_prompt(question, context)
#         return self.generate(prompt)


# # Test
# if __name__ == "__main__":
#     # Test Groq
#     llm = LLM(model_name="groq/llama-3.1-70b-versatile", language="vi")
#     response = llm.chat("Triệu chứng đau đầu và sốt có thể là bệnh gì?")
#     print(response)

import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import json

try:
    from prompt import *
except ImportError:
    from .prompt import *

load_dotenv(".env")


class LLM:
    """
    LLM wrapper supporting:
    - Google Gemini
    - Ollama (Local)
    - Groq (Optional)
    """

    def __init__(
        self,
        google_api_key=None,
        groq_api_key=None,
        temperature=0.4,
        model_name="models/gemini-2.0-flash",
        ollama_url="http://localhost:11434",
        language="vi",
    ):
        """
        Initialize LLM

        Args:
            google_api_key: Google API key
            groq_api_key: Groq API key (deprecated)
            temperature: Temperature for generation (0-1)
            model_name: Model name with provider prefix:
                - "ollama/qwen2.5:7b" (Ollama - LOCAL, RECOMMENDED)
                - "ollama/qwen2.5:7b" (Ollama - Fast local)
                - "ollama/mistral:7b" (Ollama - Good quality)
                - "models/gemini-2.0-flash" (Google Cloud)
            ollama_url: Ollama API endpoint (default: http://localhost:11434)
            language: 'vi' or 'en'
        """
        self.temperature = temperature
        self.model_name = model_name
        self.language = language.lower()
        self.ollama_url = ollama_url

        # Determine provider
        if model_name.startswith("ollama/"):
            self.provider = "ollama"
            self.model_id = model_name.replace("ollama/", "")

            # Test Ollama connection
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    available_models = [
                        m["name"] for m in response.json().get("models", [])
                    ]
                    print(
                        f"✅ Ollama connected! Available: {', '.join(available_models[:3])}..."
                    )

                    if self.model_id not in available_models:
                        print(f"⚠️ Model '{self.model_id}' not found.")
                        print(f"   Run: ollama pull {self.model_id}")
                else:
                    raise Exception(f"Ollama returned status {response.status_code}")
            except Exception as e:
                print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
                print(f"   Error: {e}")
                print(f"   Make sure Ollama is running: ollama serve")
                raise ValueError("Ollama connection failed!")

            # ✅ FIX: Print đúng provider
            print(f"✅ LLM initialized - {self.model_id}")

        else:  # Default to Gemini
            self.provider = "gemini"
            self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if not self.google_api_key:
                raise ValueError("❌ GOOGLE_API_KEY is required!")

            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=4096,
                ),
            )
            # ✅ FIX: Print đúng provider
            print(f"✅ LLM initialized: Gemini - {self.model_name}")

        print(f"   Language: {self.language}")
        print(f"   Temperature: {self.temperature}")

    def preprocess_prompt(self, question: str, context: str = None) -> str:
        """Create prompt based on language and context"""
        if self.language == "en":
            if context:
                user_message = USER_MESSAGE_WITH_CONTEXT_EN.format(
                    context=context, question=question
                )
                prompt = DEFAULT_PROMPT_EN.format(user_message=user_message)
            else:
                prompt = DEFAULT_PROMPT_EN.format(user_message=question)
        else:  # Vietnamese
            if context:
                user_message = USER_MESSAGE_WITH_CONTEXT_VN.format(
                    context=context, question=question
                )
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
            if self.provider == "ollama":
                # Ollama API
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_id,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature,
                            "num_predict": 4096,
                        },
                    },
                    timeout=120,  # 2 minutes timeout for local generation
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    error_msg = f"Ollama returned status {response.status_code}"
                    print(f"❌ {error_msg}")
                    return "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."

            else:  # Gemini
                response = self.model.generate_content(prompt)
                return response.text

        except requests.exceptions.Timeout:
            print("❌ Ollama request timeout")
            return "Xin lỗi, việc xử lý mất quá nhiều thời gian. Vui lòng thử lại."

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama")
            return (
                "Xin lỗi, không thể kết nối đến Ollama. Hãy chắc chắn Ollama đang chạy."
            )

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error generating response: {error_msg}")

            # Handle rate limits
            if "429" in error_msg or "quota" in error_msg.lower():
                return "Xin lỗi, hệ thống đang quá tải. Vui lòng thử lại sau 1 phút."

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

    def generate_stream(self, prompt: str):
        """
        Generate response with streaming (only for Ollama)

        Args:
            prompt: Input prompt

        Yields:
            Text chunks
        """
        if self.provider != "ollama":
            # Fallback to non-streaming for other providers
            yield self.generate(prompt)
            return

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_id,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": 4096,
                    },
                },
                stream=True,
                timeout=120,
            )

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if "response" in chunk:
                                yield chunk["response"]
                        except json.JSONDecodeError:
                            continue
            else:
                yield "Xin lỗi, tôi đang gặp sự cố kỹ thuật."

        except Exception as e:
            print(f"❌ Streaming error: {e}")
            yield "Xin lỗi, tôi đang gặp sự cố kỹ thuật."
