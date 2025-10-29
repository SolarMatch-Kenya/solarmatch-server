# wsgi.py

import click
from app import create_app

app = create_app()

@app.cli.command("create-admin")
@click.argument("password")
def create_admin(password):
    """Creates the default admin user for SolarMatch."""
    
    # We must run this command inside the app context
    # to get access to 'bcrypt' and 'db'
    with app.app_context():
        from extensions import db, bcrypt  # <-- IMPORT BCRYPT
        from models.user import User 
        from utils.helpers import generate_username

        ADMIN_EMAIL = "solarmatchke@gmail.com"
        
        if User.query.filter_by(email=ADMIN_EMAIL).first():
            print(f"Admin user with email {ADMIN_EMAIL} already exists.")
            print("Delete the old user first if you want to recreate them.")
            return

        full_name = "SolarMatch Admin"
        role = "admin"
        username = generate_username(full_name, role)
        
        # Hash the password with bcrypt, not werkzeug
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_admin = User(
            full_name=full_name,
            email=ADMIN_EMAIL,
            password_hash=hashed_password,
            user_name=username,
            role=role,
            password_reset_required=False,
            contract_accepted=True 
        )
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin user {ADMIN_EMAIL} created with username {username}!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {e}")