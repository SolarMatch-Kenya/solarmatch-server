from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from extensions import db, bcrypt
from models.user import User
from models.login_code import LoginCode
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta, timezone
from utils.helpers import generate_username
import random

auth_bp = Blueprint("auth", __name__)
api = Api(auth_bp)

# --- Constants ---
ADMIN_EMAILS = ["admin@solarmatch.co.ke", "trish@solarmatch.co.ke"]  # whitelist your admin emails


# -------------------------
#   REGISTER - Customer only
# -------------------------
class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        phone_number = data.get("phone_number")

        if not all([full_name, email, password]):
            return {"message": "Full name, email and password are required"}, 400

        # --- Block Admin & Installer emails from self-registration ---
        if email in ADMIN_EMAILS:
            return {"message": "Admins cannot self-register"}, 403

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"message": "Email already registered"}, 400

        # --- Default to customer role ---
        role = "customer"

        # --- Generate username ---
        user_name = generate_username(full_name, role)

        # --- Hash password ---
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            full_name=full_name,
            email=email,
            password_hash=pw_hash,
            phone_number=phone_number,
            user_name=user_name,
            role=role
        )
        db.session.add(user)
        db.session.commit()

        return {
            "message": "Customer registered successfully",
            "user_name": user_name,
            "role": role
        }, 201


# -------------------------
#   LOGIN - All roles
# -------------------------
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user_name = data.get("user_name")
        password = data.get("password")

        if not all([user_name, password]):
            return {"message": "Username and password required"}, 400

        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return {"message": "Invalid username"}, 404

        # --- Installer restriction check ---
        if user.role == "installer" and not user.password_hash:
            return {"message": "Installer login credentials not yet set"}, 403

        # --- Password check ---
        if not bcrypt.check_password_hash(user.password_hash, password):
            return {"message": "Invalid password"}, 401

        # --- Generate confirmation code ---
        code = str(random.randint(100000, 999999))
        expires = datetime.now(timezone.utc) + timedelta(minutes=5)
        login_code = LoginCode(user_id=user.id, code=code, expires_at=expires, used=False)

        db.session.add(login_code)
        db.session.commit()

        # TODO: send this via email
        print(f"Login code for {user.email}: {code}")

        return {"message": "Confirmation code sent to email"}, 200


# -------------------------
#   CONFIRM CODE (2FA)
# -------------------------
class ConfirmCodeResource(Resource):
    def post(self):
        data = request.get_json()
        user_name = data.get("user_name")
        code = data.get("code")

        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return {"message": "Invalid user"}, 404

        login_code = LoginCode.query.filter_by(user_id=user.id, code=code, used=False).first()
        now = datetime.now(timezone.utc)

        # Allow buffer for clock skew slightly
        if not login_code or login_code.expires_at.replace(tzinfo=timezone.utc) < (now - timedelta(seconds=10)):
             # Invalidate the code if expired
             if login_code:
                 login_code.used = True
                 db.session.commit()
             return {"message": "Invalid or expired code"}, 400


        login_code.used = True
        db.session.commit()

        # Generate access token using the user's ID (as confirmed before)
        access_token = create_access_token(identity=user.id) # Use ID

        # --- UPDATE THE RETURNED USER OBJECT ---
        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "user_name": user.user_name,
                "role": user.role,
                # Add these flags:
                "password_reset_required": user.password_reset_required,
                "contract_accepted": user.contract_accepted 
            }
        }, 200


# --- Register all routes ---
api.add_resource(RegisterResource, "/register")          # customer signup
api.add_resource(LoginResource, "/login")                # all roles
api.add_resource(ConfirmCodeResource, "/confirm")        # confirm code (2FA)
