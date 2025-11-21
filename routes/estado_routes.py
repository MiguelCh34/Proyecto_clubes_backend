from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Imports correctos del paquete
from .. import db
from ..database.models import Estado

estado_bp = Blueprint("estado_bp", __name__)


# ================================
#  LISTAR ESTADOS
# ================================
@estado_bp.get("/listar_estados")
@jwt_required(optional=True)
def listar_estados():
    estados = Estado.query.all()
    return jsonify([
        {"ID_Estado": e.ID_Estado, "Nombre_estado": e.Nombre_estado}
        for e in estados
    ]), 200


# ================================
#  CREAR ESTADO
# ================================
@estado_bp.post("/crear_estado")
@jwt_required()
def crear_estado():
    data = request.get_json() or {}
    name = data.get("Nombre_estado")

    if not name:
        return jsonify({"error": "Nombre_estado es obligatorio"}), 400

    if Estado.query.filter_by(Nombre_estado=name).first():
        return jsonify({"error": "Este estado ya existe"}), 400

    nuevo_estado = Estado(Nombre_estado=name)
    db.session.add(nuevo_estado)
    db.session.commit()

    return jsonify({
        "message": "Estado creado correctamente",
        "ID_Estado": nuevo_estado.ID_Estado
    }), 201


# ================================
#  OBTENER ESTADO POR ID
# ================================
@estado_bp.get("/obtener_estado/<int:id>")
@jwt_required(optional=True)
def obtener_estado(id):
    estado = Estado.query.get_or_404(id)
    return jsonify({
        "ID_Estado": estado.ID_Estado,
        "Nombre_estado": estado.Nombre_estado
    }), 200


# ================================
#  ACTUALIZAR ESTADO
# ================================
@estado_bp.put("/actualizar_estado/<int:id>")
@jwt_required()
def actualizar_estado(id):
    estado = Estado.query.get_or_404(id)
    data = request.get_json() or {}

    if "Nombre_estado" in data:
        if Estado.query.filter(Estado.Nombre_estado == data["Nombre_estado"], Estado.ID_Estado != id).first():
            return jsonify({"error": "Nombre de estado ya está en uso"}), 400
        
        estado.Nombre_estado = data["Nombre_estado"]

    db.session.commit()
    return jsonify({"message": "Estado actualizado correctamente"}), 200


# ================================
#  ELIMINAR ESTADO
# ================================
@estado_bp.delete("/eliminar_estado/<int:id>")
@jwt_required()
def eliminar_estado(id):
    estado = Estado.query.get_or_404(id)
    db.session.delete(estado)
    db.session.commit()

    return jsonify({"message": "Estado eliminado exitosamente"}), 200
