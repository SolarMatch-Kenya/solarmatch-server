from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models.user import User

password_bp = Blueprint('password', __name__)

# routes/password_routes.py

@password_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
        
    pw_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    
    user.password_hash = pw_hash
    user.password_reset_required = False # Mark as changed
    db.session.commit()
    
    # Manually create a dictionary of the user to send back
    user_data = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "user_name": user.user_name,
        "role": user.role,
        "password_reset_required": user.password_reset_required,
        "contractAccepted": user.contract_accepted
    }

    # Return the message AND the updated user object
    return jsonify({
        "message": "Password updated successfully.",
        "user": user_data  # <-- Send the updated user back
    }), 200