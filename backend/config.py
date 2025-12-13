import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"
    TESTING = os.getenv("TESTING", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///kidride_dev.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ALLOW_ORIGINS = [
        origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if origin.strip()
    ]

    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
    AUTH_DEV_BYPASS = os.getenv("AUTH_DEV_BYPASS", "true").lower() == "true"
    SERVICE_NAME = os.getenv("SERVICE_NAME", "kidride-backend")
