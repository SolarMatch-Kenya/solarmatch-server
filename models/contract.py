from extensions import db
from datetime import datetime, timezone

class SignedContract(db.Model):
    __tablename__ = 'signed_contracts'

    id = db.Column(db.Integer, primary_key=True)
    
    # This creates the link to the 'users' table
    # We use unique=True to enforce a one-to-one relationship
    # (One user can only have one signed contract)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Store the Base64 data URI of the signature image
    # db.Text is used because Base64 strings can be very long
    signature_image = db.Column(db.Text, nullable=False)
    
    ip_address = db.Column(db.String(45), nullable=True) # IPs can be IPv6
    
    # The timestamp from the frontend
    signed_at = db.Column(db.DateTime(timezone=True), nullable=False)
    
    # The timestamp when our server saved it
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<SignedContract for User {self.user_id}>'