from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from extensions import db, bcrypt
from models.user import User
from models.login_code import LoginCode
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta, timezone
import random, re

auth_bp = Blueprint("auth", __name__)
api = Api(auth_bp)

# --- Helper Functions ---
def generate_username(full_name, role):
    """Generate a friendly, role-based username."""
    first_name = re.sub(r'[^A-Za-z]', '', full_name.split()[0].capitalize())  # clean + capitalize
    random_digits = random.randint(1000, 9999)

    if role == "customer":
        prefix = "CUS"
    elif role == "installer":
        prefix = "INS"
    elif role == "admin":
        prefix = "ADM"
    else:
        prefix = "USR"

    return f"{prefix}-{first_name}-{random_digits}"

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
                "role": user.role
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
