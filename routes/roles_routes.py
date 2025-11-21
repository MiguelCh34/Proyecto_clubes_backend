from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Import correcto dentro del paquete
from .. import db
from ..database.models import Roles

roles_bp = Blueprint("roles_bp", __name__)


# ================================
#  LISTAR ROLES
# ================================
@roles_bp.get("/listar_roles")
@jwt_required(optional=True)
def listar_roles():
    roles = Roles.query.all()
    return jsonify([
        {"ID_Roles": r.ID_Roles, "Nombre_Rol": r.Nombre_Rol}
        for r in roles
    ]), 200


# ================================
#  CREAR ROL
# ================================
@roles_bp.post("/crear_rol")
@jwt_required()
def crear_rol():
    data = request.get_json() or {}
    nombre = data.get("Nombre_Rol")

    if not nombre:
        return jsonify({"error": "Nombre_Rol es obligatorio"}), 400

    if Roles.query.filter_by(Nombre_Rol=nombre).first():
        return jsonify({"error": "El rol ya existe"}), 400

    nuevo = Roles(Nombre_Rol=nombre)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "message": "Rol creado correctamente",
        "ID_Roles": nuevo.ID_Roles
    }), 201


# ================================
#  OBTENER ROL
# ================================
@roles_bp.get("/obtener_rol/<int:id>")
@jwt_required(optional=True)
def obtener_rol(id):
    r = Roles.query.get_or_404(id)
    return jsonify({
        "ID_Roles": r.ID_Roles,
        "Nombre_Rol": r.Nombre_Rol
    }), 200


# ================================
#  ACTUALIZAR ROL
# ================================
@roles_bp.put("/actualizar_rol/<int:id>")
@jwt_required()
def actualizar_rol(id):
    r = Roles.query.get_or_404(id)
    data = request.get_json() or {}

    if "Nombre_Rol" in data:
        nuevo = data["Nombre_Rol"]

        # Validar duplicado
        if Roles.query.filter(
            Roles.Nombre_Rol == nuevo,
            Roles.ID_Roles != id
        ).first():
            return jsonify({"error": "Ese nombre ya está en uso"}), 400

        r.Nombre_Rol = nuevo

    db.session.commit()
    return jsonify({"message": "Rol actualizado correctamente"}), 200


# ================================
#  ELIMINAR ROL
# ================================
@roles_bp.delete("/eliminar_rol/<int:id>")
@jwt_required()
def eliminar_rol(id):
    r = Roles.query.get_or_404(id)
    db.session.delete(r)
    db.session.commit()

    return jsonify({"message": "Rol eliminado exitosamente"}), 200
