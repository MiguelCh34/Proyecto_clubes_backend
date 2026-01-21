from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, Estado  # ← Cambiado

estado_bp = Blueprint("estado_bp", __name__)


# ================================
#  LISTAR ESTADOS
# ================================
@estado_bp.get("/listar_estados")
@jwt_required(optional=True)
def listar_estados():
    """
    Lista todos los estados.
    """
    estados = Estado.query.all()
    return jsonify([
        {
            "ID_Estado": e.ID_Estado,
            "Nombre_estado": e.Nombre_estado,  # ← Cambiar a Nombre_estado
            "Descripcion": None
        }
        for e in estados
    ]), 200


# ================================
#  CREAR ESTADO
# ================================
@estado_bp.post("/crear_estado")
@jwt_required()
@admin_required
def crear_estado():
    data = request.get_json() or {}
    
    nombre = data.get("Nombre") or data.get("Nombre_estado")

    if not nombre:
        return jsonify({"error": "Nombre es obligatorio"}), 400

    if Estado.query.filter_by(Nombre_estado=nombre).first():
        return jsonify({"error": "El estado ya existe"}), 400

    nuevo = Estado(Nombre_estado=nombre)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        "message": "Estado creado correctamente",
        "ID_Estado": nuevo.ID_Estado
    }), 201


# ================================
#  ACTUALIZAR ESTADO
# ================================
@estado_bp.put("/actualizar_estado/<int:id>")
@jwt_required()
@admin_required
def actualizar_estado(id):
    e = Estado.query.filter_by(ID_Estado=id).first_or_404()
    data = request.get_json() or {}

    if "Nombre" in data or "Nombre_estado" in data:
        nuevo = data.get("Nombre") or data.get("Nombre_estado")

        # Validar duplicado
        if Estado.query.filter(
            Estado.Nombre_estado == nuevo,
            Estado.ID_Estado != id
        ).first():
            return jsonify({"error": "Ese nombre ya está en uso"}), 400

        e.Nombre_estado = nuevo

    db.session.commit()
    return jsonify({"message": "Estado actualizado correctamente"}), 200


# ================================
#  ELIMINAR ESTADO
# ================================
@estado_bp.delete("/eliminar_estado/<int:id>")
@jwt_required()
@admin_required
def eliminar_estado(id):
    e = Estado.query.filter_by(ID_Estado=id).first_or_404()
    db.session.delete(e)
    db.session.commit()

    return jsonify({"message": "Estado eliminado exitosamente"}), 200