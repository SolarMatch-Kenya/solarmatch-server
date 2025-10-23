from ..extensions import db
from datetime import datetime

class RoofAnalysis(db.Model):
    __tablename__ = "roof_analyses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(255))
    roof_type = db.Column(db.String(100))
    monthly_bill = db.Column(db.Float)
    image_url = db.Column(db.String(512))
    solar_score = db.Column(db.Integer)
    system_size_kw = db.Column(db.Float)
    install_cost = db.Column(db.Float)
    annual_savings = db.Column(db.Float)
    roi_years = db.Column(db.Float)
    co2_saved = db.Column(db.Float)
    report_url = db.Column(db.String(512))
    ai_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("analyses", lazy=True))
