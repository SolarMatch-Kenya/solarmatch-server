from flask import Blueprint

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


@user_bp.route("/")
def index():
    return "User index"
