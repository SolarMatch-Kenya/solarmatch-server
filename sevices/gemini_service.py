import os
import google.generativeai as genai
from flask import current_app, json
import requests
import io 
import math
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
    4.  The roof type '{roof_type}' and typical orientations/angles.

    Provide the following estimates AND a suitability score in JSON format.
    The suitability score should be an integer between 0 and 100, representing
    how ideal the location and roof seem for solar, based on irradiance,
    potential orientation, and lack of obvious obstructions (guess if needed).
    Only return a single valid JSON object.

    Example format:
    {{
      "panel_count": 25,
      "annual_production_kwh": 15000,
      "annual_savings_ksh": 300000,
      "system_size_kw": 10,
      "payback_period_years": 5.5,
      "roof_orientation_ai": "South-East",
      "roof_angle_ai": 20,
      "summary_text": "Based on your {energy_kwh} kWh consumption and {roof_type} roof, we recommend a 10 kW system with 25 panels. This system is optimized for your location and provides significant energy production.",
      "financial_summary": "This 10 kW system has an estimated payback period of 5.5 years. You can expect to save approximately KSh 300,000 annually on your electricity bills, making it a strong financial investment.",
      "environmental_summary": "By installing this system, you will reduce your carbon footprint by approximately 8 tonnes of CO2 per year. This is equivalent to planting over 130 trees annually.",
      "solar_suitability_score": 92  # <-- ADDED
    }}

    JSON:
    """

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(json_text)
        if "solar_suitability_score" in data:
            try:
                score = int(data["solar_suitability_score"])
                data["solar_suitability_score"] = max(0, min(100, score)) # Clamp between 0-100
            except (ValueError, TypeError):
                 data["solar_suitability_score"] = None # Set to null if invalid
        else:
            data["solar_suitability_score"] = None # Set to null if missing

        return data
        
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
        Analyze this roof image ({roof_type} type).
        Identify the largest, flattest, most sun-facing roof plane suitable for solar panels.

        Suggest a JSON array containing position AND rotation for placing 10 standard solar panels
        (approx 1m x 2m) flat onto that identified roof plane in a grid layout.

        - 'position': [x, y, z] coordinates relative to the center of the roof plane. Assume Y is the 'up' direction perpendicular to the roof plane *at that point*.
        - 'rotation': [rx, ry, rz] Euler rotation angles IN DEGREES needed to align the panel with the roof plane. ry is rotation around the Y-axis (yaw), rx around X (pitch), rz around Z (roll).

        Estimate these values visually. Aim for a sensible layout on the main roof surface visible.
        Only return the JSON array.

        Example format:
        [
          {{"position": [-2.5, 0.05, -1.0], "rotation": [15, 0, 0]}},
          {{"position": [-2.5, 0.05, 1.0], "rotation": [15, 0, 0]}},
          {{"position": [-0.5, 0.05, -1.0], "rotation": [15, 0, 0]}},
          {{"position": [-0.5, 0.05, 1.0], "rotation": [15, 0, 0]}},
          # ... etc for 10 panels
        ]

        JSON:
        """
        
        # 10. Send BOTH the text and the image to the model
        response = model.generate_content([text_prompt, img])
        
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        layout_data = json.loads(json_text)
        
        # Validate and convert degrees to radians for three.js
        validated_layout = []
        if isinstance(layout_data, list):
            for item in layout_data:
                if isinstance(item, dict) and 'position' in item and 'rotation' in item:
                    pos = item['position']
                    rot_deg = item['rotation']
                    if (isinstance(pos, list) and len(pos) == 3 and 
                        isinstance(rot_deg, list) and len(rot_deg) == 3):
                        try:
                            # Convert rotation from degrees (AI) to radians (three.js)
                            rot_rad = [math.radians(angle) for angle in rot_deg]
                            validated_layout.append({
                                "position": [float(p) for p in pos],
                                "rotation": rot_rad 
                            })
                        except (ValueError, TypeError):
                            continue # Skip invalid number format
            return validated_layout # Return only valid items
        else:
             raise ValueError("AI did not return a list for panel layout.")
        
    except Exception as e:
        current_app.logger.error(f"Gemini AR layout failed: {e}")
        # 11. Re-raise the error so the route can catch it
        raise e