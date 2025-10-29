from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from models.contract import SignedContract
from models.quote_request import QuoteRequest
from datetime import datetime

installer_bp = Blueprint('installer', __name__)


# --- 1. ENDPOINT TO GET ALL INSTALLERS ---
@installer_bp.route('/installers', methods=['GET'])
@jwt_required() # Make sure a user is logged in to see installers
def get_all_installers():
    # Find all users who are installers and whose contract is accepted
    installers = User.query.filter_by(role='installer', contract_accepted=True).all()
    
    installer_list = []
    for inst in installers:
        installer_list.append({
            "id": inst.id,
            "name": inst.full_name,
            "location": inst.county or "N/A",
            # We'll add real ratings/reviews later
            "rating": 4.5, # Placeholder
            "reviews": (inst.id * 15) % 100 + 20 # Placeholder
        })
        
    return jsonify(installer_list), 200

# --- 2. ENDPOINT TO CREATE A QUOTE REQUEST ---
@installer_bp.route('/quote-request', methods=['POST'])
@jwt_required()
def create_quote_request():
    customer_id = get_jwt_identity()
    data = request.get_json()
    installer_id = data.get('installer_id')

    if not installer_id:
        return jsonify({"error": "Installer ID is required"}), 400

    # Check if this user is a customer
    customer = User.query.get(customer_id)
    if customer.role != 'customer':
        return jsonify({"error": "Only customers can request quotes"}), 403

    # Check if request already exists
    existing_request = QuoteRequest.query.filter_by(
        customer_id=customer_id, 
        installer_id=installer_id
    ).first()
    
    if existing_request:
        return jsonify({"message": "You have already sent a request to this installer"}), 409 # 409 Conflict

    # Create new request
    new_request = QuoteRequest(
        customer_id=customer_id,
        installer_id=installer_id,
        status='New'
    )
    
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({"message": "Quote request sent successfully!"}), 201

# --- 3. ENDPOINT FOR INSTALLER TO GET THEIR LEADS ---
@installer_bp.route('/installer-leads', methods=['GET'])
@jwt_required()
def get_installer_leads():
    installer_id = get_jwt_identity()
    
    # Ensure the user is an installer
    installer = User.query.get(installer_id)
    if installer.role != 'installer':
        return jsonify({"error": "Unauthorized"}), 403
        
    # Query all leads for this installer, and join with the customer (User) table
    # This uses the 'leads_received' relationship defined in models/user.py
    leads = installer.leads_received
    
    leads_data = []
    for lead in leads:
        leads_data.append({
            "id": lead.id,
            "status": lead.status,
            "requested_at": lead.created_at.isoformat(),
            # "customer" is the backref from the relationship
            "name": lead.customer.full_name,
            "location": lead.customer.county or "N/A",
            "contact": lead.customer.email,
            "potential": "High" # I'll add logic for this later
        })
        
    return jsonify(leads_data), 200


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