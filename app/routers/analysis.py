from flask import Blueprint, request, jsonify
from app.services import solar_api_service, gemini_service

analysis_bp = Blueprint("analysis_bp", __name__, url_prefix="/analysis")


@analysis_bp.route("/", methods=["POST"])
def get_analysis():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")

    if not lat or not lng:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    solar_data = solar_api_service.get_solar_data(lat, lng)

    if not solar_data:
        return jsonify({"error": "Could not retrieve solar data"}), 500

    ai_feedback = gemini_service.get_ai_feedback(solar_data)

    if not ai_feedback:
        return jsonify({"error": "Could not generate AI feedback"}), 500

    return jsonify({
        "solar_data": solar_data,
        "ai_feedback": ai_feedback
    })
