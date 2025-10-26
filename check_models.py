import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    # Configure the API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
    else:
        genai.configure(api_key=api_key)
        
        print("--- Your Available Models for 'generateContent' ---")
        
        # Loop through all available models
        for m in genai.list_models():
            # Check if 'generateContent' is one of the supported methods
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                
        print("--------------------------------------------------")
        print("\nUse these model names in your gemini_service.py file.")

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please ensure your GEMINI_API_KEY is correct and you have internet access.")