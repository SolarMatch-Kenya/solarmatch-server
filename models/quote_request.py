from extensions import db
from datetime import datetime, timezone

class QuoteRequest(db.Model):
    __tablename__ = 'quote_requests'

    id = db.Column(db.Integer, primary_key=True)
    
    # The ID of the customer (a User) making the request
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # The ID of the installer (also a User) receiving the request
    installer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status of the lead, e.g., "New", "Contacted", "Qualified"
    status = db.Column(db.String(50), nullable=False, default='New')

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<QuoteRequest from {self.customer_id} to {self.installer_id}>'