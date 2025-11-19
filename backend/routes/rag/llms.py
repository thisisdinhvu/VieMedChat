import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

try:
    from prompt import *
except ImportError:
    from .prompt import *

load_dotenv(".env")


class LLM:
    """
    LLM wrapper supporting:
    - Google Gemini
    - Groq (Llama, Mixtral, Gemma)
    """
    
    def __init__(self, google_api_key=None, groq_api_key=None, 
                 temperature=0.4, model_name="groq/llama-3.3-70b-versatile", 
                 language="vi"):
        """
        Initialize LLM
        
        Args:
            google_api_key: Google API key
            groq_api_key: Groq API key
            temperature: Temperature for generation (0-1)
            model_name: Model name with provider prefix:
                - "gemini-1.5-flash" (Google)
                - "groq/llama-3.3-70b-versatile" (Groq - BEST FREE)
                - "groq/llama-3.1-8b-instant" (Groq - Fastest)
                - "groq/mixtral-8x7b-32768" (Groq - Long context)
            language: 'vi' or 'en'
        """
        self.temperature = temperature
        self.model_name = model_name
        self.language = language.lower()
        
        # Determine provider
        if model_name.startswith("groq/"):
            self.provider = "groq"
            self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
            if not self.groq_api_key:
                raise ValueError("❌ GROQ_API_KEY is required!")
            
            self.client = Groq(api_key=self.groq_api_key)
            self.model_id = model_name.replace("groq/", "")
            print(f"✅ LLM initialized: Groq - {self.model_id}")
            
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
                )
            )
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
            if self.provider == "groq":
                # Groq API
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=4096,
                )
                return response.choices[0].message.content
            
            else:  # Gemini
                response = self.model.generate_content(prompt)
                return response.text
        
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


# Test
if __name__ == "__main__":
    # Test Groq
    llm = LLM(model_name="groq/llama-3.1-70b-versatile", language="vi")
    response = llm.chat("Triệu chứng đau đầu và sốt có thể là bệnh gì?")
    print(response)