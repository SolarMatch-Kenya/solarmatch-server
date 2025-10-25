from app.db.database import db
from datetime import datetime, timezone


class InstallerReview(db.Model):
    __tablename__ = "installer_reviews"

    id = db.Column(db.Integer, primary_key=True, index=True)
    installer_id = db.Column(db.Integer, db.ForeignKey("installers.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    installer = db.relationship("Installer")
    user = db.relationship("User")
