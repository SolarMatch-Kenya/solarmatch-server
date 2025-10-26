import os
import google.generativeai as genai
from flask import current_app, json
import requests
import io 
from PIL import Image

# Configure the API key from your .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_solar_analysis(address, lat, lon, energy_kwh, roof_type):
    """
    Uses Gemini to get solar panel recommendations.
    """
    # 4. Use the 'gemini-1.5-flash' model
    model = genai.GenerativeModel('models/gemini-pro-latest')

    prompt = f"""
    You are a solar installation expert for Kenya.
    Analyze the following data for a potential solar installation:

    - Location Address: "{address}"
    - Coordinates: {lat}, {lon}
    - Average Monthly Energy Consumption: {energy_kwh} kWh
    - Roof Type: "{roof_type}"

    Using this data, and considering:
    1.  Typical solar irradiance data for Kenya (specifically at {lat}, {lon}).
    2.  The user's energy consumption patterns ({energy_kwh} kWh/month).
    3.  The property's likely sunlight exposure based on its coordinates.

    Provide the following estimates in JSON format.
    Only return a single valid JSON object.

    Example format:
    {{
      "panel_count": 25,
      "annual_production_kwh": 15000,
      "annual_savings_ksh": 300000,
      "system_size_kw": 10,
      "payback_period_years": 5.5,
      "roof_orientation_ai": "South-East",
      "roof_angle_ai": 20
    }}

    JSON:
    """

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
        
    except Exception as e:
        current_app.logger.error(f"Gemini analysis failed: {e}")
        # 5. Re-raise the error so the route can catch it
        raise e 

def get_ar_layout(image_url, roof_type):
    """
    Uses Gemini to suggest a 3D layout for AR.
    """
    # 6. Use the 'gemini-1.5-flash' model
    model = genai.GenerativeModel('models/gemini-2.5-flash-image')
    
    try:
        # 7. Download the image from the URL
        image_response = requests.get(image_url)
        image_response.raise_for_status() # Raise error if download fails
        
        # 8. Open the image from the downloaded bytes
        img = Image.open(io.BytesIO(image_response.content))

        # 9. Create the text part of the prompt
        text_prompt = f"""
        Analyze this roof image.
        The roof is a "{roof_type}" type.
        
        Suggest a simple JSON array of 3D coordinates for placing 10 solar panels
        on the main, clearest surface.
        Assume a flat plane at y=0.
        
        Example format:
        [
          {{"x": -2, "z": -1}},
          {{"x": -2, "z": 1}},
          {{"x": 0, "z": -1}},
          {{"x": 0, "z": 1}},
          {{"x": 2, "z": -1}},
          {{"x": 2, "z": 1}}
        ]
        
        JSON:
        """
        
        # 10. Send BOTH the text and the image to the model
        response = model.generate_content([text_prompt, img])
        
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
        
    except Exception as e:
        current_app.logger.error(f"Gemini AR layout failed: {e}")
        # 11. Re-raise the error so the route can catch it
        raise e