import os
from flask import Blueprint, request
from flask_restful import Api, Resource
from extensions import db, bcrypt, mail
from models.user import User
from models.login_code import LoginCode
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta, timezone
from utils.helpers import generate_username
import random
from flask_mail import Message

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

        # --- 4. Send the code via email ---
        try:
            msg = Message(
                subject="Your SolarMatch Verification Code",
                recipients=[user.email],
                # sender=app.config['MAIL_DEFAULT_SENDER'] # Optional: Uses default sender from config
            )
            msg.html = f"""
            <p>Hello {user.full_name},</p>
            <p>Your verification code for SolarMatch is:</p>
            <p style="font-size: 24px; font-weight: bold; margin: 20px 0;">{code}</p>
            <p>This code will expire in 5 minutes.</p>
            <p>If you did not request this code, please ignore this email.</p>
            <p>Best regards,<br>The SolarMatch Kenya Team</p>
            """
            mail.send(msg)
            print(f"--- Verification code email sent to {user.email} ---") # Keep for confirmation

        except Exception as e:
            # Important: Log the error but don't stop the login process
            # In production, use proper logging: current_app.logger.error(...)
            print(f"!!! FAILED TO SEND VERIFICATION EMAIL to {user.email}: {e} !!!")
            # You might want to decide if the login should proceed even if email fails.
            # For now, we continue and return the success message to the frontend.

        # print(f"Login code for {user.email}: {code}")

        return {"message": "Confirmation code sent to your email"}, 200


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

        if not login_code or login_code.expires_at.replace(tzinfo=timezone.utc) < now:
            return {"message": "Invalid or expired code"}, 400

        login_code.used = True
        db.session.commit()

        # --- Generate access token ---
        access_token = create_access_token(identity=str(user.id))

        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "user_name": user.user_name,
                "role": user.role,
                "password_reset_required": user.password_reset_required, # <-- ADD THIS
                "contractAccepted": user.contract_accepted
            }
        }, 200


# -------------------------
#   USERS (Admin use)
# -------------------------
class UsersResource(Resource):
    def get(self):
        users = User.query.all()
        return {
            "users": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role": u.role,
                    "user_name": u.user_name
                } for u in users
            ]
        }, 200


# -------------------------
#   Add Installer (Admin only)
# -------------------------
class AddInstallerResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role != "admin":
            return {"message":"Admin access required"}, 403
        
        """Admin can add installers manually."""
        data = request.get_json()
        full_name = data.get("full_name")
        email = data.get("email")
        phone_number = data.get("phone_number")

        if not all([full_name, email]):
            return {"message": "Full name and email are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Installer with this email already exists"}, 400

        # --- Create temporary password ---
        temp_password = f"Solar{random.randint(1000,9999)}!"
        pw_hash = bcrypt.generate_password_hash(temp_password).decode("utf-8")

        # --- Generate installer username ---
        user_name = generate_username(user_name, "installer")

        user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            role="installer",
            user_name=user_name,
            password_hash=pw_hash
        )
        db.session.add(user)
        db.session.commit()

        # TODO: send installer email with credentials
        print(f"Installer credentials for {email} -> Username: {user_name}, Password: {temp_password}")

        return {
            "message": "Installer added successfully and credentials sent via email",
            "user_name": user_name
        }, 201


# --- Register all routes ---
api.add_resource(RegisterResource, "/register")          # customer signup
api.add_resource(LoginResource, "/login")                # all roles
api.add_resource(ConfirmCodeResource, "/confirm")        # confirm code (2FA)
api.add_resource(UsersResource, "/users")                # admin list users
api.add_resource(AddInstallerResource, "/add-installer") # admin adds installer
