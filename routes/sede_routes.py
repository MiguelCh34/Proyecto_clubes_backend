from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Import correcto dentro del paquete
from .. import db
from ..database.models import Sede


sede_bp = Blueprint("sede_bp", __name__)


# ================================
#  LISTAR SEDES
# ================================
@sede_bp.get("/listar_sedes")
@jwt_required(optional=True)
def listar_sedes():
    sedes = Sede.query.all()
    return jsonify([
        {"ID_Sede": s.ID_Sede, "Ubicacion": s.Ubicacion}
        for s in sedes
    ]), 200


# ================================
#  CREAR SEDE
# ================================
@sede_bp.post("/crear_sede")
@jwt_required()
def crear_sede():
    data = request.get_json() or {}
    ubicacion = data.get("Ubicacion")

    # Validación
    if not ubicacion:
        return jsonify({"error": "Ubicación es obligatoria"}), 400

    # Prevención de duplicados opcional (si aplica)
    if Sede.query.filter_by(Ubicacion=ubicacion).first():
        return jsonify({"error": "Ya existe una sede con esa ubicación"}), 400

    nueva = Sede(Ubicacion=ubicacion)
    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        "message": "Sede creada correctamente",
        "ID_Sede": nueva.ID_Sede
    }), 201


# ================================
#  OBTENER SEDE
# ================================
@sede_bp.get("/obtener_sede/<int:id>")
@jwt_required(optional=True)
def obtener_sede(id):
    s = Sede.query.get_or_404(id)
    return jsonify({
        "ID_Sede": s.ID_Sede,
        "Ubicacion": s.Ubicacion
    }), 200


# ================================
#  ACTUALIZAR SEDE
# ================================
@sede_bp.put("/actualizar_sede/<int:id>")
@jwt_required()
def actualizar_sede(id):
    s = Sede.query.get_or_404(id)
    data = request.get_json() or {}

    if "Ubicacion" in data:
        s.Ubicacion = data["Ubicacion"]

    db.session.commit()
    return jsonify({"message": "Sede actualizada correctamente"}), 200


# ================================
#  ELIMINAR SEDE
# ================================
@sede_bp.delete("/eliminar_sede/<int:id>")
@jwt_required()
def eliminar_sede(id):
    s = Sede.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "Sede eliminada exitosamente"}), 200
