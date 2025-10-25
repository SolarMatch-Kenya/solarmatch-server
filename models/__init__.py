# server/models/__init__.py

from .user import User
from .login_code import LoginCode

# Add these lines to make sure Flask-Migrate sees your new models
from .analysis import AnalysisRequest, AnalysisResult