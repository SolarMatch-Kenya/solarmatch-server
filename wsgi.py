import click
from app import create_app
# Used to hash the password
from werkzeug.security import generate_password_hash

app = create_app()

# --- ADD THIS CODE ---
@app.cli.command("create-admin")
@click.argument("password")
def create_admin(password):
    """Creates the default admin user for SolarMatch."""
    
    # We import here so models are loaded only when the command runs
    from extensions import db
    
    from models.user import User 
    from utils.helpers import generate_username

    ADMIN_EMAIL = "solarmatchke@gmail.com"
    
    # 1. Check if the admin already exists
    if User.query.filter_by(email=ADMIN_EMAIL).first():
        print(f"Admin user with email {ADMIN_EMAIL} already exists.")
        return

    # 2. Set all the required fields
    full_name = "SolarMatch Admin"
    role = "admin"
    username = generate_username(full_name, role)
    hashed_password = generate_password_hash(password)

    # 3. Create the new admin User object
    new_admin = User(
        full_name=full_name,
        email=ADMIN_EMAIL,
        password_hash=hashed_password,
        user_name=username,
        role=role,
        password_reset_required=False,  # As requested
        contract_accepted=True          # Bypasses contract requirement
    )
    
    # 4. Add to database and commit
    try:
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user {ADMIN_EMAIL} created with username {username}!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin: {e}")
