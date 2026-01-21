from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, ActividadesRealizadas, Persona, Actividad, Roles, Estado  # ← Cambiado


participacion_bp = Blueprint("participacion_bp", __name__)


# ================================
#  LISTAR PARTICIPACIONES
# ================================
@participacion_bp.get("/listar_participaciones")
@jwt_required(optional=True)
def listar_participaciones():
    participaciones = ActividadesRealizadas.query.all()
    return jsonify([
        {
            "ID_Participacion": p.ID_Participacion,
            "ID_Estudiante": p.ID_Estudiante,
            "ID_Actividad": p.ID_Actividad,
            "ID_Roles": p.ID_Roles,
            "ID_Estado": p.ID_Estado
        }
        for p in participaciones
    ]), 200


# ================================
#  CREAR PARTICIPACIÓN
# ================================
@participacion_bp.post("/crear_participacion")
@jwt_required()
@admin_required
def crear_participacion():
    data = request.get_json() or {}

    required_fields = ["ID_Estudiante", "ID_Actividad", "ID_Roles", "ID_Estado"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Debe enviar: ID_Estudiante, ID_Actividad, ID_Roles, ID_Estado"}), 400

    # Validaciones DB
    if not Persona.query.get(data["ID_Estudiante"]):
        return jsonify({"error": "El estudiante no existe"}), 400

    if not Actividad.query.get(data["ID_Actividad"]):
        return jsonify({"error": "La actividad no existe"}), 400

    if not Roles.query.get(data["ID_Roles"]):
        return jsonify({"error": "El rol no existe"}), 400

    if not Estado.query.get(data["ID_Estado"]):
        return jsonify({"error": "El estado no existe"}), 400

    # Restricción única
    if ActividadesRealizadas.query.filter_by(
        ID_Estudiante=data["ID_Estudiante"], 
        ID_Actividad=data["ID_Actividad"]
    ).first():
        return jsonify({"error": "Esta participación ya fue registrada"}), 400

    nueva = ActividadesRealizadas(
        ID_Estudiante=data["ID_Estudiante"],
        ID_Actividad=data["ID_Actividad"],
        ID_Roles=data["ID_Roles"],
        ID_Estado=data["ID_Estado"]
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({"message": "Participación creada", "ID_Participacion": nueva.ID_Participacion}), 201


# ================================
#  OBTENER PARTICIPACIÓN
# ================================
@participacion_bp.get("/obtener_participacion/<int:id>")
@jwt_required(optional=True)
def obtener_participacion(id):
    p = ActividadesRealizadas.query.get_or_404(id)
    return jsonify({
        "ID_Participacion": p.ID_Participacion,
        "ID_Estudiante": p.ID_Estudiante,
        "ID_Actividad": p.ID_Actividad,
        "ID_Roles": p.ID_Roles,
        "ID_Estado": p.ID_Estado
    }), 200


# ================================
#  ACTUALIZAR PARTICIPACIÓN
# ================================
@participacion_bp.put("/actualizar_participacion/<int:id>")
@jwt_required()
@admin_required
def actualizar_participacion(id):
    p = ActividadesRealizadas.query.get_or_404(id)
    data = request.get_json() or {}

    for field in ["ID_Estudiante", "ID_Actividad", "ID_Roles", "ID_Estado"]:
        if field in data:
            setattr(p, field, data[field])

    db.session.commit()
    return jsonify({"message": "Participación actualizada correctamente"}), 200


# ================================
#  ELIMINAR PARTICIPACIÓN
# ================================
@participacion_bp.delete("/eliminar_participacion/<int:id>")
@jwt_required()
@admin_required
def eliminar_participacion(id):
    p = ActividadesRealizadas.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Participación eliminada correctamente"}), 200