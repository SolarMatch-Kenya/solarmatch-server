import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    
    current_user_data = get_jwt_identity()
    if current_user_data.get('role') != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        paginated_users = User.query.filter_by(role='customer').order_by(User.created_at.desc()).paginate(
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
                "role": user.role, # This is the 'Category'
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

# TODO: Add more admin routes here
# @admin_bp.route('/stats', methods=['GET'])
# @admin_bp.route('/installers', methods=['GET'])
# @admin_bp.route('/content', methods=['GET'])