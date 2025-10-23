from flask import Blueprint, jsonify, request
from ..extensions import db
from ..models.roof_analysis import RoofAnalysis
from ..models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

analyses_bp = Blueprint("analyses", __name__)

def current_user():
    ident = get_jwt_identity()
    if not ident:
        return None
    from ..models.user import User
    return User.query.get(ident.get("id"))

@analyses_bp.route("/", methods=["POST"])
@jwt_required()
def create_analysis():
    data = request.get_json()
    user = current_user()
    if not user:
        return {"msg":"not authenticated"}, 401
    # basic validation:
    required = ["location","roof_type","monthly_bill"]
    for r in required:
        if r not in data:
            return {"msg": f"{r} is required"}, 400

    analysis = RoofAnalysis(
        user_id=user.id,
        location=data.get("location"),
        roof_type=data.get("roof_type"),
        monthly_bill=float(data.get("monthly_bill", 0)),
        image_url=data.get("image_url"),
    )
    # TODO: call AI services to fill solar_score, etc. For now, simple example:
    analysis.solar_score = data.get("solar_score", 75)
    analysis.system_size_kw = data.get("system_size_kw", 3.0)
    analysis.install_cost = data.get("install_cost", 180000)
    analysis.annual_savings = data.get("annual_savings", 56000)
    analysis.roi_years = analysis.install_cost / (analysis.annual_savings or 1)
    analysis.co2_saved = data.get("co2_saved", 600.0)

    db.session.add(analysis)
    db.session.commit()
    return jsonify({"analysis_id": analysis.id}), 201

@analyses_bp.route("/", methods=["GET"])
@jwt_required()
def list_analyses():
    user = current_user()
    if not user:
        return {"msg":"not authenticated"}, 401
    # Admins can view all, others only own
    ident = get_jwt_identity()
    if ident.get("role") == "admin":
        items = RoofAnalysis.query.order_by(RoofAnalysis.created_at.desc()).all()
    else:
        items = RoofAnalysis.query.filter_by(user_id=user.id).order_by(RoofAnalysis.created_at.desc()).all()
    out = [ {
        "id": a.id,
        "location": a.location,
        "system_size_kw": a.system_size_kw,
        "solar_score": a.solar_score,
        "created_at": a.created_at.isoformat()
    } for a in items ]
    return jsonify(out), 200

@analyses_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_analysis(id):
    a = RoofAnalysis.query.get_or_404(id)
    ident = get_jwt_identity()
    if ident.get("role") != "admin" and a.user_id != ident.get("id"):
        return {"msg":"forbidden"}, 403
    return jsonify({
        "id": a.id,
        "location": a.location,
        "roof_type": a.roof_type,
        "monthly_bill": a.monthly_bill,
        "image_url": a.image_url,
        "solar_score": a.solar_score,
        "system_size_kw": a.system_size_kw,
        "install_cost": a.install_cost,
        "annual_savings": a.annual_savings,
        "roi_years": a.roi_years,
        "co2_saved": a.co2_saved,
        "ai_summary": a.ai_summary,
        "created_at": a.created_at.isoformat()
    }), 200

@analyses_bp.route("/<int:id>", methods=["PUT","PATCH"])
@jwt_required()
def update_analysis(id):
    data = request.get_json()
    a = RoofAnalysis.query.get_or_404(id)
    ident = get_jwt_identity()
    if ident.get("role") != "admin" and a.user_id != ident.get("id"):
        return {"msg":"forbidden"}, 403
    # update allowed fields
    for field in ["location","roof_type","monthly_bill","image_url","solar_score","system_size_kw","install_cost","annual_savings","ai_summary"]:
        if field in data:
            setattr(a, field, data[field])
    db.session.commit()
    return {"msg":"updated"}, 200

@analyses_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_analysis(id):
    a = RoofAnalysis.query.get_or_404(id)
    ident = get_jwt_identity()
    if ident.get("role") != "admin" and a.user_id != ident.get("id"):
        return {"msg":"forbidden"}, 403
    db.session.delete(a)
    db.session.commit()
    return {"msg":"deleted"}, 200
