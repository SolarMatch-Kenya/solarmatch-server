from flask import Blueprint, request, jsonify, current_app, url_for
from ..extensions import db
from ..models.user import User
from ..services.email_service import send_email
from flask_jwt_extended import create_access_token
import random
import string

auth_bp = Blueprint("auth", __name__)

def _generate_code(n=6):
    return ''.join(random.choices(string.digits, k=n))

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "email already registered"}), 400

    user = User(email=email, name=name, role="customer")
    user.set_password(password)
    # generate verification code
    code = _generate_code()
    user.verification_code = code
    db.session.add(user)
    db.session.commit()

    # send verification email
    verify_link = url_for("auth.verify", _external=True)
    send_email(
        to=email,
        subject="Verify your SolarMatch account",
        body=f"Your verification code is: {code}\nOr click verify in app."
    )
    return jsonify({"msg":"registered", "user_id": user.id}), 201

@auth_bp.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    email = data.get("email")
    code = data.get("code")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg":"invalid email"}), 404
    if user.is_verified:
        return jsonify({"msg":"already verified"}), 200
    if user.verification_code == code:
        user.is_verified = True
        user.verification_code = None
        db.session.commit()
        return jsonify({"msg":"verified"}), 200
    return jsonify({"msg":"invalid code"}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg":"bad credentials"}), 401
    if not user.is_verified:
        return jsonify({"msg":"account not verified"}), 403
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"access_token": access_token, "user": {"id": user.id, "email": user.email, "role": user.role}}), 200

# Admin-only endpoints to invite installers / admins
from flask_jwt_extended import jwt_required, get_jwt_identity
import secrets

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity or identity.get("role") != "admin":
            return jsonify({"msg":"admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route("/invite-installer", methods=["POST"])
@jwt_required()
@admin_required
def invite_installer():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name", "")
    password = secrets.token_urlsafe(10)
    if User.query.filter_by(email=email).first():
        return jsonify({"msg":"user exists"}), 400
    user = User(email=email, name=name, role="installer", is_verified=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    send_email(
        to=email,
        subject="You were added to SolarMatch as an installer",
        body=f"Hi {name},\nYou were added as an installer. Login with:\nemail: {email}\npassword: {password}\nPlease change your password after first login."
    )
    return jsonify({"msg":"installer invited"}), 201

@auth_bp.route("/invite-admin", methods=["POST"])
@jwt_required()
@admin_required
def invite_admin():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name", "")
    password = secrets.token_urlsafe(12)
    if User.query.filter_by(email=email).first():
        return jsonify({"msg":"user exists"}), 400
    user = User(email=email, name=name, role="admin", is_verified=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    send_email(
        to=email,
        subject="Admin access to SolarMatch",
        body=f"Hello {name},\nYou were given admin access.\nemail: {email}\npassword: {password}"
    )
    return jsonify({"msg":"admin invited"}), 201
