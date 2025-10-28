import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "super-secret"

    # Gmail SMTP Configuration
    GMAIL_FROM_EMAIL = os.environ.get(
        "GMAIL_FROM_EMAIL") or "solarmatchke@gmail.com"
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
