from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Import correcto dentro del paquete
from .. import db
from ..database.models import Facultad

facultad_bp = Blueprint("facultad_bp", __name__)


# ================================
#  LISTAR FACULTADES
# ================================
@facultad_bp.get("/listar_facultades")
@jwt_required(optional=True)
def listar_facultades():
    facultades = Facultad.query.all()
    return jsonify([
        {"ID_Facultad": f.ID_Facultad, "Nombre": f.Nombre}
        for f in facultades
    ]), 200


# ================================
#  CREAR FACULTAD
# ================================
@facultad_bp.post("/crear_facultad")
@jwt_required()
def crear_facultad():
    data = request.get_json() or {}
    nombre = data.get("Nombre")

    if not nombre:
        return jsonify({"error": "Nombre es obligatorio"}), 400

    if Facultad.query.filter_by(Nombre=nombre).first():
        return jsonify({"error": "La facultad ya existe"}), 400

    nueva_facultad = Facultad(Nombre=nombre)
    db.session.add(nueva_facultad)
    db.session.commit()

    return jsonify({
        "message": "Facultad creada correctamente",
        "ID_Facultad": nueva_facultad.ID_Facultad
    }), 201


# ================================
#  OBTENER FACULTAD POR ID
# ================================
@facultad_bp.get("/obtener_facultad/<int:id>")
@jwt_required(optional=True)
def obtener_facultad(id):
    f = Facultad.query.get_or_404(id)
    return jsonify({
        "ID_Facultad": f.ID_Facultad,
        "Nombre": f.Nombre
    }), 200


# ================================
#  ACTUALIZAR FACULTAD
# ================================
@facultad_bp.put("/actualizar_facultad/<int:id>")
@jwt_required()
def actualizar_facultad(id):
    f = Facultad.query.get_or_404(id)
    data = request.get_json() or {}

    if "Nombre" in data:
        if Facultad.query.filter(Facultad.Nombre == data["Nombre"], Facultad.ID_Facultad != id).first():
            return jsonify({"error": "Nombre ya en uso"}), 400
        f.Nombre = data["Nombre"]

    db.session.commit()
    return jsonify({"message": "Facultad actualizada correctamente"}), 200


# ================================
#  ELIMINAR FACULTAD
# ================================
@facultad_bp.delete("/eliminar_facultad/<int:id>")
@jwt_required()
def eliminar_facultad(id):
    f = Facultad.query.get_or_404(id)

    db.session.delete(f)
    db.session.commit()

    return jsonify({"message": "Facultad eliminada exitosamente"}), 200
