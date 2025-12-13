from flask import Flask
from flask_cors import CORS

from config import Config
from firebase_admin_setup import init_firebase
from models import db
from routes import register_blueprints
from utils.helpers import json_response


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ALLOW_ORIGINS", ["*"])}})

    with app.app_context():
        init_firebase(app)
        register_blueprints(app)

    @app.route("/health", methods=["GET"])
    def health():
        return json_response({"status": "ok", "service": app.config.get("SERVICE_NAME", "kidride-backend")})

    @app.route("/api/v1/ping", methods=["GET"])
    def ping():
        return json_response({"message": "pong"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
