from extensions import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String,)
    user_name = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String, default="customer")    # can be a customer, or installer
    county = db.Column(db.String(100), nullable=True)
    password_reset_required = db.Column(db.Boolean, default=False, nullable=False)
    installer_category = db.Column(db.String(100), nullable=True) # e.g., Residential, Commercial

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # relationships
    # analysis = db.relationship("Analysis", backref="user", lazy=True)
    login_codes = db.relationship("LoginCode", backref="user", lazy=True)

    