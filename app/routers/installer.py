from flask import Blueprint

installer_bp = Blueprint("installer_bp", __name__, url_prefix="/installer")


@installer_bp.route("/")
def index():
    return "Installer index"
