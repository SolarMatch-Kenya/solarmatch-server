from flask import Blueprint

ai_bp = Blueprint("ai_bp", __name__, url_prefix="/ai")


@ai_bp.route("/")
def index():
    return "AI index"
