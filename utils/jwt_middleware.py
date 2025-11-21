from functools import wraps
from flask import request, jsonify
import jwt

SECRET_KEY = "MI_SECRETO_JWT_123"

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = data["user_id"]
        except:
            return jsonify({"error": "Token inválido o expirado"}), 401

        return f(*args, **kwargs)

    return decorated
