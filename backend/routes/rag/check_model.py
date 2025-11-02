# check_gemini_models.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

print("="*60)
print("🔍 Available Gemini Models")
print("="*60)

try:
    # List all available models
    models = genai.list_models()
    
    generation_models = []
    embedding_models = []
    
    for model in models:
        # Filter models that support generateContent
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model.name)
        
        # Filter models that support embedContent
        if 'embedContent' in model.supported_generation_methods:
            embedding_models.append(model.name)
    
    print("\n✅ Models supporting TEXT GENERATION (generateContent):")
    print("-" * 60)
    for i, model_name in enumerate(generation_models, 1):
        print(f"{i}. {model_name}")
    
    print("\n✅ Models supporting EMBEDDINGS (embedContent):")
    print("-" * 60)
    for i, model_name in enumerate(embedding_models, 1):
        print(f"{i}. {model_name}")
    
    print("\n" + "="*60)
    print(f"Total generation models: {len(generation_models)}")
    print(f"Total embedding models: {len(embedding_models)}")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")