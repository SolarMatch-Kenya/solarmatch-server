from app.db.database import db


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
