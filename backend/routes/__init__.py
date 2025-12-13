from flask import Flask

from .auth_routes import auth_bp
from .household_routes import household_bp
from .kid_routes import kid_bp
from .user_routes import user_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(user_bp, url_prefix="/api/v1/users")
    app.register_blueprint(kid_bp, url_prefix="/api/v1/kids")
    app.register_blueprint(household_bp, url_prefix="/api/v1/households")
