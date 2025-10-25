from app.db.database import db
from datetime import datetime, timezone


class RoofAnalysis(db.Model):
    __tablename__ = "roof_analyses"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    address = db.Column(db.String, index=True)
    roof_type = db.Column(db.String)
    monthly_bill = db.Column(db.Float)
    image_url = db.Column(db.String)
    solar_score = db.Column(db.Float)
    system_size_kw = db.Column(db.Float)
    install_cost = db.Column(db.Float)
    annual_savings = db.Column(db.Float)
    roi_years = db.Column(db.Float)
    co2_saved = db.Column(db.Float)
    report_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ai_summary = db.Column(db.Text)
