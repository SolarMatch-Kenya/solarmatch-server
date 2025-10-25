import os
import cloudinary.uploader
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from ..models import AnalysisRequest, AnalysisResult
from ..sevices.gemini_service import get_solar_analysis, get_ar_layout

# Configure Cloudinary (it reads from CLOUDINARY_URL in .env)
import .cloudinary

# ... in your main app factory ...
# cloudinary.config(
#   cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
#   api_key = os.environ.get('CLOUDINARY_API_KEY'),
#   api_secret = os.environ.get('CLOUDINARY_API_SECRET')
# )
# Or just let it use the URL

@main.route('/api/analysis/submit', methods=['POST'])
@jwt_required()
def submit_analysis():
    current_user_id = get_jwt_identity()
    
    # 1. Get data from the form
    # Note: FormData sends files and text separately
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
    
    # --- 4. Run AI Analysis (This should be an async task!) ---
    # For simplicity, we run it synchronously.
    # In production, use Celery or RQ.
    
    try:
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
            panel_layout_json=json.dumps(ar_layout_json) # Store as JSON string
        )
        db.session.add(new_result)
        db.session.commit()
        
        return jsonify({"message": "Analysis submitted successfully", "analysis_id": new_request.id}), 201

    except Exception as e:
        # If AI fails, update status
        new_request.result = AnalysisResult(request_id=new_request.id, status='FAILED')
        db.session.commit()
        return jsonify({"error": f"AI analysis failed: {e}"}), 500

@main.route('/api/analysis/latest', methods=['GET'])
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
            "panel_layout": json.loads(result.panel_layout_json) # Parse JSON string back to object
        }
    }), 200