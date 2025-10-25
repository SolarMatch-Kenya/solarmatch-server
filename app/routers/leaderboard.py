from flask import Blueprint

leaderboard_bp = Blueprint("leaderboard_bp", __name__, url_prefix="/leaderboard")


@leaderboard_bp.route("/")
def index():
    return "Leaderboard index"
