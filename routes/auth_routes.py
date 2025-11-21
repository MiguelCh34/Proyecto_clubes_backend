from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
from ..database.models import Usuario

auth_bp = Blueprint("auth_bp", __name__)


# ============================
#   REGISTER
# ============================
@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    if not nombre or not email or not password:
        return jsonify({"error": "nombre, email y password son obligatorios"}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "Este email ya está registrado"}), 409

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"message": "Usuario registrado correctamente"}), 201



# ============================
#   LOGIN
# ============================
@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email y password necesarios"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.password_hash, password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # 👇 Se fuerza a que identity sea STRING
    access_token = create_access_token(identity=str(usuario.ID_Usuario))
    refresh_token = create_refresh_token(identity=str(usuario.ID_Usuario))

    return jsonify({
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200



# ============================
#   REFRESH TOKEN
# ============================
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    # Devuelve string → convertir a int si lo necesitas
    user_id = int(get_jwt_identity())
    
    new_token = create_access_token(identity=str(user_id))

    return jsonify({"access_token": new_token}), 200



# ============================
#   CURRENT USER INFO
# ============================
@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())  # Convertir a entero para consultas
    
    usuario = Usuario.query.get_or_404(user_id)

    return jsonify({
        "ID_Usuario": usuario.ID_Usuario,
        "nombre": usuario.nombre,
        "email": usuario.email
    }), 200
