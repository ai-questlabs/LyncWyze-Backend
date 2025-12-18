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

    # Log DB target on startup to eliminate ambiguity in container logs.
    # Redact password if present (e.g., postgresql+psycopg2://user:pass@host/db).
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if isinstance(db_uri, str):
        redacted = db_uri
        if "://" in redacted and "@" in redacted:
            scheme, rest = redacted.split("://", 1)
            creds_and_host, tail = rest.split("@", 1)
            if ":" in creds_and_host:
                user = creds_and_host.split(":", 1)[0]
                redacted = f"{scheme}://{user}:***@{tail}"
        app.logger.info("SQLALCHEMY_DATABASE_URI=%s", redacted)

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
