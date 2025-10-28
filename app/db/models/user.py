from app.db.database import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    location = db.Column(db.String)
    role = db.Column(db.String, default="customer")
    reset_token = db.Column(db.String, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_reset_token(self, token):
        """Set reset token with 1 hour expiration"""
        from datetime import timedelta
        self.reset_token = token
        self.reset_token_expires = datetime.now(
            timezone.utc) + timedelta(hours=1)

    def is_reset_token_valid(self, token):
        """Check if reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        # Ensure both datetimes are timezone-aware for comparison
        current_time = datetime.now(timezone.utc)
        expires_time = self.reset_token_expires

        # If expires_time is naive, make it timezone-aware
        if expires_time.tzinfo is None:
            expires_time = expires_time.replace(tzinfo=timezone.utc)

        if current_time > expires_time:
            return False
        return self.reset_token == token

    def clear_reset_token(self):
        """Clear reset token after successful password reset"""
        self.reset_token = None
        self.reset_token_expires = None
