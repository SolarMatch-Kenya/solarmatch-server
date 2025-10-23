from ..extensions import db
from datetime import datetime
from passlib.hash import bcrypt

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer")  # 'customer' | 'installer' | 'admin'
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship("Installer", secondary="user_favorites", back_populates="favorited_by")

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)
