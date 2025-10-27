from extensions import db # Assuming you have db = SQLAlchemy() in your __init__.py
from sqlalchemy.sql import func

class AnalysisRequest(db.Model):
    __tablename__ = 'analysis_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    energy_consumption = db.Column(db.Integer)
    roof_type_manual = db.Column(db.String(50)) # User's selection
    roof_image_url = db.Column(db.String(500)) # URL from Cloudinary
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # Relationship to the results
    result = db.relationship('AnalysisResult', backref='request', uselist=False, lazy=True)

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('analysis_requests.id'), nullable=False, unique=True)
    
    # --- AI-Generated Data ---
    status = db.Column(db.String(50), default='PENDING') # e.g., PENDING, COMPLETED, FAILED
    roof_type_ai = db.Column(db.String(50))
    roof_orientation_ai = db.Column(db.String(50))
    roof_angle_ai = db.Column(db.Float)
    
    panel_count = db.Column(db.Integer)
    annual_production_kwh = db.Column(db.Float)
    annual_savings_ksh = db.Column(db.Float)
    system_size_kw = db.Column(db.Float)
    payback_period_years = db.Column(db.Float)
    
    # For the 3D/AR view
    panel_layout_json = db.Column(db.Text) # Stores a JSON string of panel coordinates
    roof_model_url = db.Column(db.String(500), nullable=True)

    # --- NEW FIELDS FOR TAB CONTENT ---
    summary_text = db.Column(db.Text, nullable=True)
    financial_summary_text = db.Column(db.Text, nullable=True)
    environmental_summary_text = db.Column(db.Text, nullable=True)