from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

# Importaciones corregidas para estructura de paquete
from .. import db
from ..database.models import Inscripcion, Persona, Club, Roles, Estado, Usuario

inscripcion_bp = Blueprint("inscripcion_bp", __name__)


# ================================
#  LISTAR INSCRIPCIONES
# ================================
@inscripcion_bp.get("/listar_inscripciones")
@jwt_required(optional=True)
def listar_inscripciones():
    inscripciones = Inscripcion.query.all()
    return jsonify([
        {
            "ID_Inscripcion": i.ID_Inscripcion,
            "ID_Persona": i.ID_Persona,
            "ID_Club": i.ID_Club,
            "Fecha_Ingreso": i.Fecha_Ingreso.isoformat() if i.Fecha_Ingreso else None
        }
        for i in inscripciones
    ]), 200


# ================================
#  CREAR INSCRIPCIÓN
# ================================
@inscripcion_bp.post("/crear_inscripcion")
@jwt_required()
def crear_inscripcion():
    data = request.get_json() or {}

    required = ["ID_Persona", "ID_Club", "ID_Roles", "ID_Estado", "ID_Usuario"]

    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios: ID_Persona, ID_Club, ID_Roles, ID_Estado, ID_Usuario"}), 400

    # Validación existencias
    if not Persona.query.get(data["ID_Persona"]):
        return jsonify({"error": "La persona no existe"}), 400

    if not Club.query.get(data["ID_Club"]):
        return jsonify({"error": "El club no existe"}), 400

    if not Roles.query.get(data["ID_Roles"]):
        return jsonify({"error": "El rol no existe"}), 400

    if not Estado.query.get(data["ID_Estado"]):
        return jsonify({"error": "El estado no existe"}), 400

    if not Usuario.query.get(data["ID_Usuario"]):
        return jsonify({"error": "El usuario no existe"}), 400

    # Validación única (bool prevent)
    if Inscripcion.query.filter_by(ID_Persona=data["ID_Persona"], ID_Club=data["ID_Club"]).first():
        return jsonify({"error": "Esa persona ya está inscrita en ese club"}), 400

    insc = Inscripcion(
        ID_Persona=data["ID_Persona"],
        ID_Club=data["ID_Club"],
        ID_Roles=data["ID_Roles"],
        ID_Estado=data["ID_Estado"],
        ID_Usuario=data["ID_Usuario"],
        Fecha_Ingreso=datetime.utcnow()
    )

    db.session.add(insc)
    db.session.commit()

    return jsonify({"message": "Inscripción creada correctamente", "ID_Inscripcion": insc.ID_Inscripcion}), 201


# ================================
#  OBTENER UNA INSCRIPCIÓN
# ================================
@inscripcion_bp.get("/obtener_inscripcion/<int:id>")
@jwt_required(optional=True)
def obtener_inscripcion(id):
    i = Inscripcion.query.get_or_404(id)
    return jsonify({
        "ID_Inscripcion": i.ID_Inscripcion,
        "ID_Persona": i.ID_Persona,
        "ID_Club": i.ID_Club,
        "ID_Roles": i.ID_Roles,
        "ID_Estado": i.ID_Estado,
        "ID_Usuario": i.ID_Usuario,
        "Fecha_Ingreso": i.Fecha_Ingreso.isoformat() if i.Fecha_Ingreso else None
    }), 200


# ================================
#  ACTUALIZAR INSCRIPCIÓN
# ================================
@inscripcion_bp.put("/actualizar_inscripcion/<int:id>")
@jwt_required()
def actualizar_inscripcion(id):
    insc = Inscripcion.query.get_or_404(id)
    data = request.get_json() or {}

    for field in ["ID_Persona", "ID_Club", "ID_Roles", "ID_Estado", "ID_Usuario"]:
        if field in data:
            setattr(insc, field, data[field])

    db.session.commit()

    return jsonify({"message": "Inscripción actualizada correctamente"}), 200


# ================================
#  ELIMINAR INSCRIPCIÓN
# ================================
@inscripcion_bp.delete("/eliminar_inscripcion/<int:id>")
@jwt_required()
def eliminar_inscripcion(id):
    insc = Inscripcion.query.get_or_404(id)
    db.session.delete(insc)
    db.session.commit()

    return jsonify({"message": "Inscripción eliminada exitosamente"}), 200
