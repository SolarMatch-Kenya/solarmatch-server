# src/tasks.py
import json
from extensions import db 
from models.analysis import AnalysisRequest, AnalysisResult
from sevices.gemini_service import get_solar_analysis, get_ar_layout
from celery_config import celery 
from app import app

@celery.task(name='tasks.run_ai_analysis')
def run_ai_analysis(request_id):
    """
    The background task that runs all slow AI analysis.
    """
    from routes.ai_routes import get_3d_roof_model

    try:
        # Get the request and result objects
        req = AnalysisRequest.query.get(request_id)
        res = AnalysisResult.query.filter_by(request_id=request_id).first()

        if not req or not res:
            print(f"Task failed: Could not find request_id {request_id}")
            app.logger.error(f"Task failed: Could not find request or result for ID {request_id}")
            return

        # Run the slow AI/API calls
        roof_model_url = get_3d_roof_model(lat=req.latitude, lon=req.longitude)
        
        gemini_data = get_solar_analysis(
            address=req.address,
            lat=req.latitude,
            lon=req.longitude,
            energy_kwh=req.energy_consumption,
            roof_type=req.roof_type_manual
        )
        
        ar_layout_json = get_ar_layout(
            image_url=req.roof_image_url,
            roof_type=req.roof_type_manual
        )

        # Update the result object with the new data
        res.status = 'COMPLETED'
        res.roof_type_ai = gemini_data.get('roof_type_ai', req.roof_type_manual)
        res.roof_orientation_ai = gemini_data.get('roof_orientation_ai')
        res.roof_angle_ai = gemini_data.get('roof_angle_ai')
        res.panel_count = gemini_data.get('panel_count')
        res.annual_production_kwh = gemini_data.get('annual_production_kwh')
        res.annual_savings_ksh = gemini_data.get('annual_savings_ksh')
        res.system_size_kw = gemini_data.get('system_size_kw')
        res.payback_period_years = gemini_data.get('payback_period_years')
        res.panel_layout_json = json.dumps(ar_layout_json)
        res.roof_model_url = roof_model_url
        res.summary_text = gemini_data.get('summary_text')
        res.financial_summary_text = gemini_data.get('financial_summary_text')
        res.environmental_summary_text = gemini_data.get('environmental_summary_text')
        res.solar_suitability_score = gemini_data.get('solar_suitability_score')

        # Commit to the database
        db.session.commit()
        print(f"Successfully processed analysis {request_id}")

    except Exception as e:
        # If anything fails, mark the task as FAILED
        db.session.rollback()
        if res:
            res.status = 'FAILED'
            db.session.commit()
        print(f"Failed to process analysis {request_id}: {e}")