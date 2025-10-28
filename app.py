import os
from flask import Flask
from flask_restful import Api
from extensions import db, migrate
from flask_cors import CORS
from config import Config
from extensions import db, migrate, bcrypt, jwt, mail
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.password_routes import password_bp
from routes.installer_routes import installer_bp
from routes.contact_routes import contact_bp
from routes import HelloResource


def create_app(config_class=Config):
    app = Flask(__name__)

    FRONTEND_URL = os.environ.get('FRONTEND_URL')
    ALLOWED_ORIGINS = [FRONTEND_URL, "http://localhost:5173"] 

    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(password_bp, url_prefix="/api/auth")
    app.register_blueprint(installer_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api")

    # Setup API
    api = Api(app)

    api.add_resource(HelloResource, "/api/hello")

    from routes.test_routes import test_bp
    app.register_blueprint(test_bp, url_prefix="/api/test")


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)