from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.contract import SignedContract
from datetime import datetime

installer_bp = Blueprint('installer', __name__)

@installer_bp.route('/installers/<int:user_id>/contract', methods=['POST'])
@jwt_required()
def sign_contract(user_id):
    
    # --- Security Check ---
    # Get the ID from the JWT token
    current_user_id = get_jwt_identity()
    
    # Ensure the user ID in the URL matches the one in the token
    # A user cannot sign a contract for someone else
    if str(user_id) != current_user_id:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    if user.role != 'installer':
        return jsonify({"error": "Only installers can sign this contract"}), 403

    # Check if they already signed
    if user.contract_accepted:
        return jsonify({"message": "Contract already signed"}), 400

    data = request.get_json()
    signature = data.get('signature')
    ip_address = data.get('ipAddress')
    signed_at_str = data.get('signedAt') # This is an ISO string from frontend

    if not all([signature, ip_address, signed_at_str]):
        return jsonify({"error": "Missing signature, IP, or timestamp"}), 400

    # Convert the ISO string from JS into a Python datetime object
    # The 'Z' (Zulu time) is replaced with '+00:00' for Py's fromisoformat
    try:
        signed_at_dt = datetime.fromisoformat(signed_at_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400
        
    # --- This is the main logic ---
    
    # 1. Create the new contract record
    new_contract = SignedContract(
        user_id=user.id,
        signature_image=signature,
        ip_address=ip_address,
        signed_at=signed_at_dt
    )

    # 2. Update the user's status
    user.contract_accepted = True

    try:
        db.session.add(new_contract)
        db.session.commit()
        
        # We need to return the updated user, just like we did for
        # password change, so the AuthContext stays in sync.
        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "user_name": user.user_name,
            "role": user.role,
            "password_reset_required": user.password_reset_required,
            "contractAccepted": user.contract_accepted # This will now be true
        }
        
        return jsonify({
            "message": "Contract signed successfully",
            "user": user_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error signing contract: {e}") # for debugging
        return jsonify({"error": "Database error"}), 500