from flask import Blueprint, request, jsonify
from app.services import user_service, email_service
from app.db.models import User
from app.db import db
from flask_jwt_extended import create_access_token
from flask_cors import cross_origin

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User with this email already exists"}), 409

    try:
        user = user_service.create_user(name, email, password)
        return jsonify({"message": "User created successfully", "user": {"id": user.id, "name": user.name, "email": user.email}}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173", "http://localhost:5174"], supports_credentials=True)
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, user={"id": user.id, "name": user.name, "email": user.email, "role": user.role}), 200


@auth_bp.route("/forgot-password", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173", "http://localhost:5174"], supports_credentials=True)
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Missing email"}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        try:
            # Generate a secure reset token
            import secrets
            reset_token = secrets.token_urlsafe(32)

            # Store reset token in user model
            user.set_reset_token(reset_token)
            db.session.commit()

            # Send password reset email
            email_sent = email_service.send_password_reset_email(
                user.email, reset_token)

            if email_sent:
                return jsonify({"message": "Password reset email sent successfully"}), 200
            else:
                return jsonify({"error": "Failed to send password reset email"}), 500

        except Exception as e:
            return jsonify({"error": f"Failed to process password reset: {str(e)}"}), 500

    # Always return success message for security (don't reveal if email exists)
    return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200


@auth_bp.route("/reset-password", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173", "http://localhost:5174"], supports_credentials=True)
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("newPassword")

    if not token or not new_password:
        return jsonify({"error": "Missing token or new password"}), 400

    # Find user by reset token
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Validate token
    if not user.is_reset_token_valid(token):
        return jsonify({"error": "Invalid or expired reset token"}), 400

    try:
        # Update password and clear reset token
        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()

        return jsonify({"message": "Password reset successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to reset password: {str(e)}"}), 500


@auth_bp.route("/")
def index():
    return "Auth index"
