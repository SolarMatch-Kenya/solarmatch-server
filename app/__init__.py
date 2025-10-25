from flask import Flask
from app.db import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.db.models import User, Admin, Installer, RoofAnalysis, Contract, Leaderboard, InstallerReview, FinancePartner, SolarData
from app.routers.admin import admin_bp
from app.routers.ai import ai_bp
from app.routers.analysis import analysis_bp
from app.routers.ar import ar_bp
from app.routers.auth import auth_bp
from app.routers.installer import installer_bp
from app.routers.leaderboard import leaderboard_bp
from app.routers.public import public_bp
from app.routers.user import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.core.config.Config")

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    with app.app_context():
        # Register Blueprints
        app.register_blueprint(admin_bp)
        app.register_blueprint(ai_bp)
        app.register_blueprint(analysis_bp)
        app.register_blueprint(ar_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(installer_bp)
        app.register_blueprint(leaderboard_bp)
        app.register_blueprint(public_bp)
        app.register_blueprint(user_bp)

        return app
