from extensions import db
from datetime import datetime, timezone
from .contract import SignedContract
from .quote_request import QuoteRequest

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

    contract_accepted = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # relationships
    # analysis = db.relationship("Analysis", backref="user", lazy=True)
    login_codes = db.relationship("LoginCode", backref="user", lazy=True)
    contract = db.relationship("SignedContract", backref="user", uselist=False, lazy=True)
    requests_sent = db.relationship('QuoteRequest', foreign_keys=[QuoteRequest.customer_id], backref='customer', lazy=True)
    
    # Leads RECEIVED by this user (when they are an installer)
    leads_received = db.relationship('QuoteRequest', foreign_keys=[QuoteRequest.installer_id], backref='installer', lazy=True)

    