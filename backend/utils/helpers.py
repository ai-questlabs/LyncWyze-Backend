from typing import Any, Dict, Optional

from flask import jsonify, request


def json_response(payload: Dict[str, Any], status_code: int = 200):
    response = jsonify(payload)
    response.status_code = status_code
    return response


def error_response(message: str, status_code: int = 400, errors: Optional[Dict[str, Any]] = None):
    body = {"error": message}
    if errors:
        body["details"] = errors
    return json_response(body, status_code=status_code)


def get_bearer_token() -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    from flask import current_app
    
    if not auth_header.lower().startswith("bearer "):
        current_app.logger.debug("Authorization header missing or not Bearer type")
        return None
    token = auth_header.split(" ", 1)[1].strip() or None
    if token:
        current_app.logger.debug("Bearer token extracted successfully")
    else:
        current_app.logger.debug("Bearer token was empty after extraction")
    return token
