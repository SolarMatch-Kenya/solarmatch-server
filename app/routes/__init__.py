from .auth import auth_bp
from .analyses import analyses_bp
from .installers import installers_bp
from .uploads import uploads_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(analyses_bp, url_prefix="/analyses")
    app.register_blueprint(installers_bp, url_prefix="/installers")
    app.register_blueprint(uploads_bp, url_prefix="/upload")

