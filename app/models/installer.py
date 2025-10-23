from ..extensions import db
from datetime import datetime

class Installer(db.Model):
    __tablename__ = "installers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    county = db.Column(db.String(100))
    contact_info = db.Column(db.String(255))
    services = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    rating_avg = db.Column(db.Float, default=0.0)
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    experience_years = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorited_by = db.relationship("User", secondary="user_favorites", back_populates="favorites")
