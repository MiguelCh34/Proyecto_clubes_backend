from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required
from datetime import datetime
from database.models import db, Actividad, Club, Estado, Usuario

actividad_bp = Blueprint("actividad_bp", __name__)


# ================================
#  LISTAR ACTIVIDADES
# ================================
@actividad_bp.get("/listar_actividades")
@jwt_required(optional=True)
def listar_actividades():
    actividades = Actividad.query.all()
    return jsonify([
        {
            "ID_Actividad": a.ID_Actividad,
            "Nombre": a.Nombre,
            "Descripcion": a.Descripcion,
            "Lugar": a.Lugar,
            "Fecha": a.Fecha.isoformat() if a.Fecha else None,
            "ID_Club": a.ID_Club,
            "ID_Estado": a.ID_Estado,
            "ID_Usuario": a.ID_Usuario
        }
        for a in actividades
    ]), 200


# ================================
#  CREAR ACTIVIDAD
# ================================
@actividad_bp.post("/crear_actividad")
@jwt_required()
@admin_required
def crear_actividad():
    data = request.get_json() or {}

    campos_obligatorios = ["Nombre", "Fecha", "ID_Club", "ID_Estado", "ID_Usuario"]

    if not all(campo in data for campo in campos_obligatorios):
        return jsonify({"error": "Campos requeridos: Nombre, Fecha, ID_Club, ID_Estado, ID_Usuario"}), 400

    try:
        fecha_dt = datetime.fromisoformat(data["Fecha"])
    except:
        return jsonify({"error": "Formato de fecha inválido, use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}), 400

    if not Club.query.get(data["ID_Club"]):
        return jsonify({"error": "El club no existe"}), 400

    if not Estado.query.get(data["ID_Estado"]):
        return jsonify({"error": "El estado no existe"}), 400

    if not Usuario.query.get(data["ID_Usuario"]):
        return jsonify({"error": "El usuario no existe"}), 400

    nueva = Actividad(
        Nombre=data["Nombre"],
        Descripcion=data.get("Descripcion"),
        Fecha=fecha_dt,
        Lugar=data.get("Lugar"),
        ID_Club=data["ID_Club"],
        ID_Estado=data["ID_Estado"],
        ID_Usuario=data["ID_Usuario"]
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({"message": "Actividad creada", "ID_Actividad": nueva.ID_Actividad}), 201


# ================================
#  OBTENER ACTIVIDAD POR ID
# ================================
@actividad_bp.get("/obtener_actividad/<int:id>")
@jwt_required(optional=True)
def obtener_actividad(id):
    a = Actividad.query.get_or_404(id)

    return jsonify({
        "ID_Actividad": a.ID_Actividad,
        "Nombre": a.Nombre,
        "Descripcion": a.Descripcion,
        "Fecha": a.Fecha.isoformat() if a.Fecha else None,
        "Lugar": a.Lugar
    }), 200


# ================================
#  ACTUALIZAR ACTIVIDAD
# ================================
@actividad_bp.put("/actualizar_actividad/<int:id>")
@jwt_required()
@admin_required
def actualizar_actividad(id):
    a = Actividad.query.get_or_404(id)
    data = request.get_json() or {}

    if "Fecha" in data:
        try:
            a.Fecha = datetime.fromisoformat(data["Fecha"])
        except:
            return jsonify({"error": "Fecha inválida"}), 400

    for campo in ["Nombre", "Descripcion", "Lugar", "ID_Club", "ID_Estado", "ID_Usuario"]:
        if campo in data:
            setattr(a, campo, data[campo])

    db.session.commit()

    return jsonify({"message": "Actividad actualizada correctamente"}), 200


# ================================
#  ELIMINAR ACTIVIDAD
# ================================
@actividad_bp.delete("/eliminar_actividad/<int:id>")
@jwt_required()
@admin_required
def eliminar_actividad(id):
    a = Actividad.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message": "Actividad eliminada"}), 200