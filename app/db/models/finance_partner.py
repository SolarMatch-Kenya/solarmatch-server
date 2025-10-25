from app.db.database import db


class FinancePartner(db.Model):
    __tablename__ = "finance_partners"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    type = db.Column(db.String)
    loan_terms = db.Column(db.String)
    interest_rate = db.Column(db.String)
    contact_info = db.Column(db.String)
    verified = db.Column(db.Boolean, default=False)
