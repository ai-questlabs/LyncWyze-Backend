import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials
from flask import Flask

firebase_app: Optional[firebase_admin.App] = None


def init_firebase(app: Flask) -> Optional[firebase_admin.App]:
    global firebase_app

    if firebase_app:
        return firebase_app

    cred_path = app.config.get("FIREBASE_CREDENTIALS_PATH")
    if not cred_path:
        app.logger.warning("FIREBASE_CREDENTIALS_PATH not set; Firebase admin not initialized")
        return None

    try:
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred)
        app.logger.info("Firebase admin initialized")
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Firebase admin initialization failed: %s", exc)
        logging.exception(exc)
        firebase_app = None
    return firebase_app
