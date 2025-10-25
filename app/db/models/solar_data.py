from app.db.database import db
from datetime import datetime, timezone


class SolarData(db.Model):
    __tablename__ = "solar_data"

    id = db.Column(db.Integer, primary_key=True, index=True)
    county = db.Column(db.String, index=True)
    avg_sun_hours = db.Column(db.Float)
    panel_efficiency = db.Column(db.Float)
    irradiance_kwm2 = db.Column(db.Float)
    avg_temp = db.Column(db.Float)
    last_updated = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
