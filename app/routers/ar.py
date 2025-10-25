from flask import Blueprint

ar_bp = Blueprint("ar_bp", __name__, url_prefix="/ar")


@ar_bp.route("/")
def index():
    return "AR index"
