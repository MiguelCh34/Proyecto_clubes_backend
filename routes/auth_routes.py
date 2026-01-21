from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from utils.decorators import admin_required

from database.models import db, Usuario, Persona, Rol

auth_bp = Blueprint("auth_bp", __name__)


# ============================
#   REGISTER
# ============================
@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    nombre = data.get("nombre")
    apellido = data.get("apellido", "")
    email = data.get("email")
    password = data.get("password")
    celular = data.get("celular", "")

    if not nombre or not email or not password:
        return jsonify({"error": "nombre, email y password son obligatorios"}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "Este email ya está registrado"}), 409

    # Crear usuario
    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        password_hash=generate_password_hash(password),
        rol='usuario'
    )
    
    db.session.add(nuevo_usuario)
    db.session.flush()  # Para obtener el ID antes del commit

    # Obtener el rol "Usuario" de la tabla Rol
    rol_usuario = Rol.query.filter_by(nombre_rol='Usuario').first()
    if not rol_usuario:
        rol_usuario = Rol.query.get(2)  # Fallback al ID 2

    # Crear persona asociada
    nueva_persona = Persona(
        id_usuario=nuevo_usuario.ID_Usuario,
        nombre=nombre,
        apellido=apellido,
        correo_electronico=email,
        celular=celular,
        id_rol=rol_usuario.id_rol if rol_usuario else 2
    )
    
    db.session.add(nueva_persona)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado correctamente",
        "usuario": {
            "id": nuevo_usuario.ID_Usuario,
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol
        }
    }), 201



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

    access_token = create_access_token(
        identity=str(usuario.ID_Usuario),
        additional_claims={
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    )
    
    refresh_token = create_refresh_token(identity=str(usuario.ID_Usuario))

    return jsonify({
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id": usuario.ID_Usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }), 200



# ============================
#   REFRESH TOKEN
# ============================
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = int(get_jwt_identity())
    
    usuario = Usuario.query.get(user_id)
    
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    new_token = create_access_token(
        identity=str(user_id),
        additional_claims={
            "email": usuario.email,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    )

    return jsonify({"access_token": new_token}), 200



# ============================
#   CURRENT USER INFO
# ============================
@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    
    usuario = Usuario.query.get_or_404(user_id)

    return jsonify({
        "ID_Usuario": usuario.ID_Usuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol
    }), 200


# ============================
#   ACTUALIZAR USUARIO (ADMIN)
# ============================
@auth_bp.put("/actualizar_usuario/<int:id>")
@jwt_required()
@admin_required
def actualizar_usuario(id):
    """
    Permite a un admin actualizar nombre, email y rol de un usuario
    """
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json() or {}

    # Validar email único
    if "email" in data and Usuario.query.filter(
        Usuario.email == data["email"],
        Usuario.ID_Usuario != id
    ).first():
        return jsonify({"error": "Este email ya está en uso"}), 400

    # Actualizar campos
    if "nombre" in data:
        usuario.nombre = data["nombre"]
    
    if "email" in data:
        usuario.email = data["email"]
    
    if "rol" in data and data["rol"] in ["admin", "usuario"]:
        usuario.rol = data["rol"]

    db.session.commit()

    return jsonify({
        "message": "Usuario actualizado correctamente",
        "usuario": {
            "id": usuario.ID_Usuario,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }), 200


# ============================
#   ELIMINAR USUARIO (ADMIN)
# ============================
@auth_bp.delete("/eliminar_usuario/<int:id>")
@jwt_required()
@admin_required
def eliminar_usuario(id):
    """
    Permite a un admin eliminar un usuario
    """
    usuario = Usuario.query.get_or_404(id)
    
    # Evitar que el admin se elimine a sí mismo
    user_id = int(get_jwt_identity())
    if user_id == id:
        return jsonify({"error": "No puedes eliminarte a ti mismo"}), 400

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"message": "Usuario eliminado correctamente"}), 200