from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User

installer_bp = Blueprint('installer', __name__)

@installer_bp.route('/contract', methods=['POST'])
@jwt_required()
def submit_contract():
    user_id = get_jwt_identity()
    installer = User.query.get(user_id)

    if not installer or installer.role != 'installer':
        return jsonify({"error": "Installer not found or invalid role"}), 403

    # Basic check - in reality, you might save signature data, IP, etc.
    # For now, just mark as accepted.
    installer.contract_accepted = True
    db.session.commit()
    
    return jsonify({"message": "Contract submitted successfully"}), 200

# Add other installer-specific routes here later (e.g., getting leads)