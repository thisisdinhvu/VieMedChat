import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def call_gemini(messages):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt= "Bạn là trợ lý AI thông minh và thân thiện.\n\n"
        
        for msg in messages:
            if msg['role'] == 'user':
                prompt += f"Người dùng: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                prompt += f"Trợ lý: {msg['content']}\n"
        
        prompt += "Trợ lý: "
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {str(e)}")
        raise Exception("Lỗi khi gọi Gemini API")