import os
import google.generativeai as genai
from flask import current_app, json

# Configure the API key from your .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Function to analyze the roof image
def analyze_roof_image(image_url):
    """
    Uses Gemini to analyze a roof image from a URL.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    # You need to fetch the image data from the URL to send to Gemini
    # For Cloudinary, you can just pass the URL.
    # Let's assume you fetch the image bytes first if needed,
    # but for many cloud URLs, Gemini can fetch it.
    
    # A simple way (if Gemini can access the URL):
    # image_part = {
    #     'mime_type': 'image/jpeg', # or png
    #     'data': <image_bytes> 
    # }
    
    # For this example, let's assume a simpler prompt if Gemini Vision can access URLs
    # NOTE: This is a complex task. You might need a more specialized model
    # or to use the user's `handlePhotoUpload` API call instead.
    
    # Let's pivot: Your frontend *already* has an API for this: /api/ai/roof-photo
    # Let's assume that API (which you have) returns the data.
    # This function will focus on the *text-based* analysis.
    pass # We will skip this for now, as your form already calls /api/ai/roof-geometry

def get_solar_analysis(address, lat, lon, energy_kwh, roof_type):
    """
    Uses Gemini to get solar panel recommendations.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

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
        # ... (rest of your function) ...
        response = model.generate_content(prompt)
        # Clean up the response to get just the JSON
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
        
    except Exception as e:
        current_app.logger.error(f"Gemini analysis failed: {e}")
        return None

def get_ar_layout(image_url, roof_type):
    """
    Uses Gemini to suggest a 3D layout for AR.
    This is an advanced task.
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    # This is a very simplified example.
    # Real 3D mapping is complex.
    # We will ask Gemini for a simple grid layout.
    prompt = f"""
    Analyze this roof image: {image_url}
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
    
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
        
    except Exception as e:
        current_app.logger.error(f"Gemini AR layout failed: {e}")
        return None # Return an empty layout