import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # --- Flask-Mail Configuration for Gmail ---
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587 # Use 465 for SSL, 587 for TLS
    MAIL_USE_TLS = True # Use TLS (recommended)
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # Your Gmail address
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # Your Gmail App Password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') # Sender email shown to recipient
    # ----------------------------------------