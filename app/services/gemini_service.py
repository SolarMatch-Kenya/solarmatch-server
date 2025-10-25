import google.generativeai as genai
from flask import current_app


def get_ai_feedback(solar_data):
    api_key = current_app.config["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-pro")

    prompt = f"Based on the following solar data, provide a natural language summary and recommendation for a homeowner in Kenya:\n\n{solar_data}"

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
