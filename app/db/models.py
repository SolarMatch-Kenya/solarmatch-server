from app.db.database import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    location = db.Column(db.String)
    role = db.Column(db.String, default="customer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)


class Installer(db.Model):
    __tablename__ = "installers"

    id = db.Column(db.Integer, primary_key=True, index=True)
    company_name = db.Column(db.String, index=True)
    county = db.Column(db.String)
    contact_person = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    phone = db.Column(db.String)
    service_areas = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)
    rating_avg = db.Column(db.Float)
    website = db.Column(db.String)
    logo_url = db.Column(db.String)


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_summary = db.Column(db.Text)


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True, index=True)
    signature = db.Column(db.String)  # Base64 encoded image
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    user = db.relationship("User")


class Leaderboard(db.Model):
    __tablename__ = "leaderboards"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_savings = db.Column(db.Float)
    total_co2_reduced = db.Column(db.Float)
    rank = db.Column(db.Integer)


class InstallerReview(db.Model):
    __tablename__ = "installer_reviews"

    id = db.Column(db.Integer, primary_key=True, index=True)
    installer_id = db.Column(db.Integer, db.ForeignKey("installers.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    installer = db.relationship("Installer")
    user = db.relationship("User")


class FinancePartner(db.Model):
    __tablename__ = "finance_partners"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    type = db.Column(db.String)
    loan_terms = db.Column(db.String)
    interest_rate = db.Column(db.String)
    contact_info = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)


class SolarData(db.Model):
    __tablename__ = "solar_data"

    id = db.Column(db.Integer, primary_key=True, index=True)
    county = db.Column(db.String, index=True)
    avg_sun_hours = db.Column(db.Float)
    panel_efficiency = db.Column(db.Float)
    irradiance_kwm2 = db.Column(db.Float)
    avg_temp = db.Column(db.Float)
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
