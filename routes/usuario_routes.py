# backend_clubes/routes/usuario_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import admin_required
from database.models import db, Usuario
from services.usuario_service import (
    listar_usuarios as svc_listar,
    obtener_usuario as svc_obtener,
    actualizar_usuario as svc_actualizar,
)

usuario_bp = Blueprint("usuario_bp", __name__)

@usuario_bp.get("/listar_usuarios")
@jwt_required()
def listar_usuarios():
    users = svc_listar()
    return jsonify([{"ID_Usuario": u.ID_Usuario, "nombre": u.nombre, "email": u.email} for u in users])

@usuario_bp.get("/mi_usuario")
@jwt_required()
def mi_usuario():
    uid = int(get_jwt_identity())
    u = svc_obtener(uid)
    return jsonify({"ID_Usuario": u.ID_Usuario, "nombre": u.nombre, "email": u.email})

@usuario_bp.get("/obtener_usuario/<int:id>")
@jwt_required()
def obtener_usuario(id):
    u = svc_obtener(id)
    return jsonify({"ID_Usuario": u.ID_Usuario, "nombre": u.nombre, "email": u.email})

@usuario_bp.put("/actualizar_usuario/<int:id>")
@jwt_required()
def actualizar_usuario(id):
    u = svc_obtener(id)
    data = request.get_json() or {}
    error = svc_actualizar(u, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Usuario actualizado"})

@usuario_bp.delete("/eliminar_usuario/<int:id>")
@jwt_required()
def eliminar_usuario(id):
    u = svc_obtener(id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})

# ================================
#  CAMBIAR CONTRASEÑA
# ================================
@usuario_bp.put("/cambiar_contrasena")
@jwt_required()
def cambiar_contrasena():
    """Permite al usuario cambiar su contraseña"""
    from werkzeug.security import check_password_hash, generate_password_hash
    
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    if not all(k in data for k in ['contrasena_actual', 'contrasena_nueva']):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    
    usuario = Usuario.query.get(current_user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Verificar contraseña actual
    if not check_password_hash(usuario.Contrasena, data['contrasena_actual']):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 400
    
    # Actualizar contraseña
    usuario.Contrasena = generate_password_hash(data['contrasena_nueva'])
    db.session.commit()
    
    return jsonify({"message": "Contraseña actualizada exitosamente"}), 200