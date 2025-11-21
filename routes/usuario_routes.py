# backend_clubes/routes/usuario_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..database.models import Usuario
from ..services.usuario_service import (
    listar_usuarios as svc_listar,
    obtener_usuario as svc_obtener,
    actualizar_usuario as svc_actualizar,
)
from .. import db

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
