from flask import Blueprint

public_bp = Blueprint("public_bp", __name__, url_prefix="/")


@public_bp.route("/")
def index():
    return "Public index"
