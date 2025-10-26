import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from sqlalchemy import or_ # <-- 1. Import 'or_' for searching
import random
from utils.helpers import generate_username
from extensions import bcrypt
from models.content import Faq, SustainabilityTip, AboutContent

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


# --- INSTALLER MANAGEMENT (NEW) ---

@admin_bp.route('/installers', methods=['GET'])
@jwt_required()
def get_all_installers():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    search_term = request.args.get('search', '', type=str)
    
    try:
        query = User.query.filter_by(role='installer')
        if search_term:
            query = query.filter(or_(User.full_name.ilike(f"%{search_term}%"), User.email.ilike(f"%{search_term}%"), User.county.ilike(f"%{search_term}%")))
        
        installers = query.order_by(User.full_name).all()
        
        installers_list = []
        for user in installers:
            installers_list.append({
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "county": user.county,
                "category": user.installer_category
            })
        return jsonify({"installers": installers_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/installers', methods=['POST'])
@jwt_required()
def add_installer():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403
        
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    county = data.get("county")
    installer_category = data.get("installer_category")

    if not all([full_name, email, phone_number, county, installer_category]):
        return jsonify({"message": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Installer with this email already exists"}), 400

    # --- Create temporary password ---
    temp_password = f"Solar{random.randint(1000,9999)}!"
    pw_hash = bcrypt.generate_password_hash(temp_password).decode("utf-8")

    user_name = generate_username(full_name, "installer")

    user = User(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        county=county,
        role="installer",
        user_name=user_name,
        password_hash=pw_hash,
        password_reset_required=True, # <-- Force password change
        installer_category=installer_category
    )
    db.session.add(user)
    db.session.commit()

    # --- IMPORTANT ---
    # In a real app, you would email this. For now, we print it to the console
    # so you can test the installer login flow.
    print("--- NEW INSTALLER CREATED ---")
    print(f"Email: {email}")
    print(f"Username: {user_name}")
    print(f"Temporary Password: {temp_password}")
    print("-------------------------------")

    return jsonify({
        "message": "Installer added successfully",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email, "category": user.installer_category}
    }), 201

@admin_bp.route('/installers/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_installer(user_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin':
        return jsonify({"error": "Admin access required"}), 403

    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        return jsonify({"error": "User not found"}), 404
        
    if user_to_delete.role != 'installer':
        return jsonify({"error": "This user is not an installer"}), 400
        
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify({"message": "Installer deleted successfully"}), 200


# --- CONTENT MANAGEMENT (NEW) ---

# --- FAQs ---
@admin_bp.route('/faqs', methods=['GET'])
@jwt_required()
def get_faqs():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    faqs = Faq.query.order_by(Faq.created_at).all()
    return jsonify({"faqs": [{"id": f.id, "question": f.question, "answer": f.answer} for f in faqs]}), 200

@admin_bp.route('/faqs', methods=['POST'])
@jwt_required()
def add_faq():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({"error": "Question and answer are required"}), 400
        
    new_faq = Faq(question=data['question'], answer=data['answer'])
    db.session.add(new_faq)
    db.session.commit()
    return jsonify({"id": new_faq.id, "question": new_faq.question, "answer": new_faq.answer}), 201

@admin_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
@jwt_required()
def update_faq(faq_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    faq = Faq.query.get(faq_id)
    if not faq: return jsonify({"error": "FAQ not found"}), 404
    
    data = request.get_json()
    if not data or ('question' not in data and 'answer' not in data):
        return jsonify({"error": "Question or answer is required"}), 400
        
    if 'question' in data: faq.question = data['question']
    if 'answer' in data: faq.answer = data['answer']
    db.session.commit()
    return jsonify({"id": faq.id, "question": faq.question, "answer": faq.answer}), 200

@admin_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
@jwt_required()
def delete_faq(faq_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    faq = Faq.query.get(faq_id)
    if not faq: return jsonify({"error": "FAQ not found"}), 404
        
    db.session.delete(faq)
    db.session.commit()
    return jsonify({"message": "FAQ deleted"}), 200

# --- Sustainability Tips --- (Similar structure to FAQs)
@admin_bp.route('/tips', methods=['GET'])
@jwt_required()
def get_tips():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    tips = SustainabilityTip.query.order_by(SustainabilityTip.created_at).all()
    return jsonify({"tips": [{"id": t.id, "title": t.title, "description": t.description} for t in tips]}), 200

@admin_bp.route('/tips', methods=['POST'])
@jwt_required()
def add_tip():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    if not data or 'title' not in data or 'description' not in data:
        return jsonify({"error": "Title and description are required"}), 400
        
    new_tip = SustainabilityTip(title=data['title'], description=data['description'])
    db.session.add(new_tip)
    db.session.commit()
    return jsonify({"id": new_tip.id, "title": new_tip.title, "description": new_tip.description}), 201
    
@admin_bp.route('/tips/<int:tip_id>', methods=['PUT'])
@jwt_required()
def update_tip(tip_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    tip = SustainabilityTip.query.get(tip_id)
    if not tip: return jsonify({"error": "Tip not found"}), 404
    
    data = request.get_json()
    if not data or ('title' not in data and 'description' not in data):
        return jsonify({"error": "Title or description is required"}), 400
        
    if 'title' in data: tip.title = data['title']
    if 'description' in data: tip.description = data['description']
    db.session.commit()
    return jsonify({"id": tip.id, "title": tip.title, "description": tip.description}), 200

@admin_bp.route('/tips/<int:tip_id>', methods=['DELETE'])
@jwt_required()
def delete_tip(tip_id):
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    tip = SustainabilityTip.query.get(tip_id)
    if not tip: return jsonify({"error": "Tip not found"}), 404
        
    db.session.delete(tip)
    db.session.commit()
    return jsonify({"message": "Tip deleted"}), 200

# --- About Page Content ---
@admin_bp.route('/about', methods=['GET'])
@jwt_required() # Technically not needed if About page is public, but good practice for admin edit
def get_about_content():
    # Find the content, or create it if it doesn't exist
    content = AboutContent.query.get(1)
    if not content:
        content = AboutContent(id=1, mission="", vision="")
        db.session.add(content)
        db.session.commit()
    return jsonify({"mission": content.mission, "vision": content.vision}), 200

@admin_bp.route('/about', methods=['PUT'])
@jwt_required()
def update_about_content():
    admin_user = User.query.get(get_jwt_identity())
    if not admin_user or admin_user.role != 'admin': return jsonify({"error": "Admin access required"}), 403
    
    content = AboutContent.query.get(1)
    if not content: return jsonify({"error": "About content not found"}), 404 # Should not happen
    
    data = request.get_json()
    if not data or ('mission' not in data and 'vision' not in data):
         return jsonify({"error": "Mission or vision content is required"}), 400
         
    if 'mission' in data: content.mission = data['mission']
    if 'vision' in data: content.vision = data['vision']
    db.session.commit()
    return jsonify({"mission": content.mission, "vision": content.vision}), 200