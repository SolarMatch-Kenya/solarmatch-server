import os
import json
import cloudinary.uploader
from flask import request, jsonify, Blueprint, current_app
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.analysis import AnalysisRequest, AnalysisResult
from sevices.gemini_service import get_solar_analysis, get_ar_layout

# Configure Cloudinary (it reads from CLOUDINARY_URL in .env)
import cloudinary

# --- Define the Blueprint ---
ai_bp = Blueprint('ai', __name__) # <-- Create the blueprint

def get_3d_roof_model(lat, lon):
    """
    Calls the Google Aerial View API to get a 3D model URL.
    """
    try:
        maps_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not maps_key:
            current_app.logger.error("GOOGLE_MAPS_API_KEY not set.")
            return None
            
        url = "https://aerialview.googleapis.com/v1/buildings:findClosest"
        params = {
            'key': maps_key,
            'location.latitude': lat,
            'location.longitude': lon
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an error for bad responses
        
        data = response.json()
        
        # Extract the GLB model URL
        model_url = data.get('renders', {}).get('gltf', {}).get('url')
        return model_url
        
    except Exception as e:
        current_app.logger.error(f"Aerial View API failed: {e}")
        return None

# --- Use the Blueprint for routing ---
@ai_bp.route('/analysis/submit', methods=['POST']) # <-- Changed from @main.route
@jwt_required()
def submit_analysis():
    current_user_id = get_jwt_identity()
    
    # 1. Get data from the form
    form_data = request.form
    roof_image_file = request.files.get('roofImage')

    if not roof_image_file:
        return jsonify({"error": "Roof image is required"}), 400

    # 2. Upload image to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(
            roof_image_file,
            folder="roof_analysis"
        )
        image_url = upload_result.get('secure_url')
    except Exception as e:
        return jsonify({"error": f"Image upload failed: {e}"}), 500

    # 3. Save the initial request to DB
    new_request = AnalysisRequest(
        user_id=current_user_id,
        address=form_data.get('address'),
        latitude=float(form_data.get('latitude', 0)),
        longitude=float(form_data.get('longitude', 0)),
        energy_consumption=int(form_data.get('energyConsumption')),
        roof_type_manual=form_data.get('roofType'),
        roof_image_url=image_url
    )
    db.session.add(new_request)
    db.session.commit()
    
    # --- 4. Run AI Analysis (Async task recommended) ---
    try:
        roof_model_url = get_3d_roof_model(
            lat=new_request.latitude,
            lon=new_request.longitude
        )

        # Get text-based analysis
        gemini_data = get_solar_analysis(
            address=new_request.address,
            lat=new_request.latitude,
            lon=new_request.longitude,
            energy_kwh=new_request.energy_consumption,
            roof_type=new_request.roof_type_manual
        )
        
        # Get AR layout
        ar_layout_json = get_ar_layout(
            image_url=new_request.roof_image_url,
            roof_type=new_request.roof_type_manual
        )

        # 5. Save results to DB
        new_result = AnalysisResult(
            request_id=new_request.id,
            status='COMPLETED',
            roof_type_ai=gemini_data.get('roof_type_ai', new_request.roof_type_manual),
            roof_orientation_ai=gemini_data.get('roof_orientation_ai'),
            roof_angle_ai=gemini_data.get('roof_angle_ai'),
            panel_count=gemini_data.get('panel_count'),
            annual_production_kwh=gemini_data.get('annual_production_kwh'),
            annual_savings_ksh=gemini_data.get('annual_savings_ksh'),
            system_size_kw=gemini_data.get('system_size_kw'),
            payback_period_years=gemini_data.get('payback_period_years'),
            panel_layout_json=json.dumps(ar_layout_json),
            roof_model_url=roof_model_url
        )
        db.session.add(new_result)
        db.session.commit()
        
        return jsonify({"message": "Analysis submitted successfully", "analysis_id": new_request.id}), 201

    except Exception as e:
        # If AI fails, update status
        # Check if result already exists before creating a new one
        if not new_request.result:
             new_request.result = AnalysisResult(request_id=new_request.id, status='FAILED')
        else:
             new_request.result.status = 'FAILED'
        db.session.commit()
        return jsonify({"error": f"AI analysis failed: {e}"}), 500

@ai_bp.route('/analysis/latest', methods=['GET']) # <-- Changed from @main.route
@jwt_required()
def get_latest_analysis():
    """
    Fetches the most recent analysis for the logged-in user.
    """
    current_user_id = get_jwt_identity()
    
    latest_request = AnalysisRequest.query.filter_by(user_id=current_user_id).order_by(AnalysisRequest.created_at.desc()).first()
    
    if not latest_request:
        return jsonify({"error": "No analysis found"}), 404
        
    if not latest_request.result or latest_request.result.status == 'PENDING':
        return jsonify({"status": "PENDING", "message": "Your analysis is still processing."}), 202
        
    if latest_request.result.status == 'FAILED':
        return jsonify({"status": "FAILED", "message": "The analysis could not be completed."}), 500

    # Success! Return all data
    result = latest_request.result
    return jsonify({
        "status": "COMPLETED",
        "request": {
            "address": latest_request.address,
            "energy_consumption": latest_request.energy_consumption,
            "roof_image_url": latest_request.roof_image_url
        },
        "result": {
            "panel_count": result.panel_count,
            "annual_production_kwh": result.annual_production_kwh,
            "annual_savings_ksh": result.annual_savings_ksh,
            "system_size_kw": result.system_size_kw,
            "payback_period_years": result.payback_period_years,
            "panel_layout": json.loads(result.panel_layout_json) if result.panel_layout_json else None,
            "roof_model_url": result.roof_model_url
        }
    }), 200