from flask import Flask
from flask_restful import Api
from extensions import db, migrate
from flask_cors import CORS
from config import Config
from extensions import db, migrate, bcrypt, jwt

# Import resources
# from routes.auth_routes import RegisterResource, LoginResource
# from routes.return_routes import ReturnResource
from routes.auth_routes import auth_bp
from routes import HelloResource

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5173", "http://localhost:5173"])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register routes
    # from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Setup API
    api = Api(app)
    # api.add_resource(RegisterResource, "/api/auth/register")
    # api.add_resource(LoginResource, "/api/auth/login")
    # api.add_resource(ReturnResource, "/api/returns")

    api.add_resource(HelloResource, "/api/hello")

    from routes.test_routes import test_bp
    app.register_blueprint(test_bp, url_prefix="/api/test")


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)