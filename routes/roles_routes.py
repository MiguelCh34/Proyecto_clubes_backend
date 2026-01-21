from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, Roles  # ← Cambiado


roles_bp = Blueprint("roles_bp", __name__)


# ================================
#  LISTAR ROLES
# ================================
@roles_bp.get("/listar_roles")
@jwt_required(optional=True)
def listar_roles():
    roles = Roles.query.all()
    return jsonify([
        {
            "ID_Rol": r.ID_Roles,        # ← CAMBIO: Retorna ID_Rol (lo que espera el frontend)
            "Nombre": r.Nombre_Rol,      # ← CAMBIO: Retorna Nombre (lo que espera el frontend)
            "Descripcion": None          # ← AGREGADO: Para compatibilidad
        }
        for r in roles
    ]), 200


# ================================
#  CREAR ROL
# ================================
@roles_bp.post("/crear_rol")
@jwt_required()
@admin_required
def crear_rol():
    data = request.get_json() or {}
    
    # El frontend envía "Nombre", lo convertimos a "Nombre_Rol" para la BD
    nombre = data.get("Nombre") or data.get("Nombre_Rol")  # ← Acepta ambos

    if not nombre:
        return jsonify({"error": "Nombre es obligatorio"}), 400

    if Roles.query.filter_by(Nombre_Rol=nombre).first():
        return jsonify({"error": "El rol ya existe"}), 400

    nuevo = Roles(Nombre_Rol=nombre)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "message": "Rol creado correctamente",
        "ID_Rol": nuevo.ID_Roles  # ← CAMBIO: Retorna ID_Rol
    }), 201


# ================================
#  OBTENER ROL
# ================================
@roles_bp.get("/obtener_rol/<int:id>")
@jwt_required(optional=True)
def obtener_rol(id):
    r = Roles.query.filter_by(ID_Roles=id).first_or_404()  # ← CAMBIO: Busca por ID_Roles
    return jsonify({
        "ID_Rol": r.ID_Roles,      # ← CAMBIO: Retorna ID_Rol
        "Nombre": r.Nombre_Rol,    # ← CAMBIO: Retorna Nombre
        "Descripcion": None
    }), 200


# ================================
#  ACTUALIZAR ROL
# ================================
@roles_bp.put("/actualizar_rol/<int:id>")
@jwt_required()
@admin_required
def actualizar_rol(id):
    r = Roles.query.filter_by(ID_Roles=id).first_or_404()  # ← CAMBIO: Busca por ID_Roles
    data = request.get_json() or {}

    # El frontend envía "Nombre", lo convertimos a "Nombre_Rol"
    if "Nombre" in data or "Nombre_Rol" in data:
        nuevo = data.get("Nombre") or data.get("Nombre_Rol")  # ← Acepta ambos

        # Validar duplicado
        if Roles.query.filter(
            Roles.Nombre_Rol == nuevo,
            Roles.ID_Roles != id
        ).first():
            return jsonify({"error": "Ese nombre ya está en uso"}), 400

        r.Nombre_Rol = nuevo

    # Manejar Descripcion si existe (aunque no está en tu BD)
    if "Descripcion" in data:
        pass  # Tu tabla no tiene este campo

    db.session.commit()
    return jsonify({"message": "Rol actualizado correctamente"}), 200


# ================================
#  ELIMINAR ROL
# ================================
@roles_bp.delete("/eliminar_rol/<int:id>")
@jwt_required()
@admin_required
def eliminar_rol(id):
    r = Roles.query.filter_by(ID_Roles=id).first_or_404()  # ← CAMBIO: Busca por ID_Roles
    db.session.delete(r)
    db.session.commit()

    return jsonify({"message": "Rol eliminado exitosamente"}), 200