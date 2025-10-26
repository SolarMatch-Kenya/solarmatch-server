import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from sqlalchemy import or_ # <-- 1. Import 'or_' for searching

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    
    current_user_id = get_jwt_identity() # <-- Note: We know this is the ID now
    
    admin_user = User.query.get(current_user_id)
    
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    # --- 2. Add Search and Filter Logic ---
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    search_term = request.args.get('search', '', type=str)
    
    try:
        # Start with the base query
        query = User.query.filter(
            or_(User.role == 'customer', User.role == 'banned') # Show customers and banned users
        )
        
        # Add search if provided
        if search_term:
            # Search by name, email, or even ID
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%"),
                    User.user_name.ilike(f"%{search_term}%")
                )
            )
            
        # TODO: Add county/category filters here later
        
        paginated_users = query.order_by(User.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        users = paginated_users.items
        
        users_list = []
        for user in users:
            users_list.append({
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "county": user.county,
                "role": user.role,
                "created_at": user.created_at.isoformat()
            })

        return jsonify({
            "users": users_list,
            "pagination": {
                "current_page": paginated_users.page,
                "total_pages": paginated_users.pages,
                "total_users": paginated_users.total
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. Add New Routes for Banning/Unbanning ---

@admin_bp.route('/users/<int:user_id>/ban', methods=['PUT'])
@jwt_required()
def ban_user(user_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403
        
    user_to_ban = User.query.get(user_id)
    if not user_to_ban:
        return jsonify({"error": "User not found"}), 404
    
    # You can't ban other admins
    if user_to_ban.role == 'admin':
        return jsonify({"error": "Cannot ban an admin"}), 403
        
    user_to_ban.role = 'banned'
    db.session.commit()
    return jsonify({"message": f"User {user_to_ban.full_name} has been banned"}), 200

@admin_bp.route('/users/<int:user_id>/unban', methods=['PUT'])
@jwt_required()
def unban_user(user_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403
        
    user_to_unban = User.query.get(user_id)
    if not user_to_unban:
        return jsonify({"error": "User not found"}), 404
    
    if user_to_unban.role == 'banned':
        user_to_unban.role = 'customer' # Revert them to customer
        db.session.commit()
        return jsonify({"message": f"User {user_to_unban.full_name} has been unbanned"}), 200
    
    return jsonify({"error": "User is not currently banned"}), 400