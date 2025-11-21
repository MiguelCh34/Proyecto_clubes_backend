from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Import correcto dentro del paquete
from .. import db
from ..database.models import Persona, Estado, Usuario

persona_bp = Blueprint("persona_bp", __name__)


# ================================
#  LISTAR PERSONAS
# ================================
@persona_bp.get("/listar_personas")
@jwt_required(optional=True)
def listar_personas():
    personas = Persona.query.all()
    return jsonify([
        {
            "ID_Persona": p.ID_Persona,
            "Nombre": p.Nombre,
            "Apellido": p.Apellido,
            "Correo_institucional": p.Correo_institucional,
            "Cedula": p.Cedula,
            "Edad": p.Edad,
            "Telefono": p.Telefono,
            "ID_Estado": p.ID_Estado,
            "ID_Usuario": p.ID_Usuario
        }
        for p in personas
    ]), 200


# ================================
#  CREAR PERSONA
# ================================
@persona_bp.post("/crear_persona")
@jwt_required()
def crear_persona():
    data = request.get_json() or {}
    required = ["Nombre", "Apellido", "ID_Estado", "ID_Usuario"]

    if not all(field in data for field in required):
        return jsonify({"error": "Debe enviar: Nombre, Apellido, ID_Estado e ID_Usuario"}), 400

    # Validaciones FK
    if not Estado.query.get(data["ID_Estado"]):
        return jsonify({"error": "El estado no existe"}), 400

    if not Usuario.query.get(data["ID_Usuario"]):
        return jsonify({"error": "El usuario no existe"}), 400

    # Validaciones únicas
    if data.get("Correo_institucional") and Persona.query.filter_by(Correo_institucional=data["Correo_institucional"]).first():
        return jsonify({"error": "Correo institucional ya registrado"}), 400

    if data.get("Cedula") and Persona.query.filter_by(Cedula=data["Cedula"]).first():
        return jsonify({"error": "Cédula ya registrada"}), 400

    nueva = Persona(
        Nombre=data["Nombre"],
        Apellido=data["Apellido"],
        Carrera=data.get("Carrera"),
        Correo_institucional=data.get("Correo_institucional"),
        Cantidad=data.get("Cantidad", 1),
        Edad=data.get("Edad"),
        Cedula=data.get("Cedula"),
        Telefono=data.get("Telefono"),
        ID_Estado=data["ID_Estado"],
        ID_Usuario=data["ID_Usuario"]
    )

    db.session.add(nueva)
    db.session.commit()

    return jsonify({"message": "Persona creada correctamente", "ID_Persona": nueva.ID_Persona}), 201


# ================================
#  OBTENER UNA PERSONA
# ================================
@persona_bp.get("/obtener_persona/<int:id>")
@jwt_required(optional=True)
def obtener_persona(id):
    p = Persona.query.get_or_404(id)
    return jsonify({
        "ID_Persona": p.ID_Persona,
        "Nombre": p.Nombre,
        "Apellido": p.Apellido,
        "Correo_institucional": p.Correo_institucional,
        "Cedula": p.Cedula,
        "Edad": p.Edad
    }), 200


# ================================
#  ACTUALIZAR PERSONA
# ================================
@persona_bp.put("/actualizar_persona/<int:id>")
@jwt_required()
def actualizar_persona(id):
    p = Persona.query.get_or_404(id)
    data = request.get_json() or {}

    # Previene duplicados en actualizaciones
    if "Correo_institucional" in data and Persona.query.filter(
        Persona.Correo_institucional == data["Correo_institucional"],
        Persona.ID_Persona != id
    ).first():
        return jsonify({"error": "Correo ya en uso por otra persona"}), 400

    if "Cedula" in data and Persona.query.filter(
        Persona.Cedula == data["Cedula"],
        Persona.ID_Persona != id
    ).first():
        return jsonify({"error": "Cedula ya pertenece a otra persona"}), 400

    # Actualizar campos permitidos
    for field in ["Nombre", "Apellido", "Carrera", "Correo_institucional", "Cantidad",
                  "Edad", "Cedula", "Telefono", "ID_Estado", "ID_Usuario"]:
        if field in data:
            setattr(p, field, data[field])

    db.session.commit()
    return jsonify({"message": "Persona actualizada correctamente"}), 200


# ================================
#  ELIMINAR PERSONA
# ================================
@persona_bp.delete("/eliminar_persona/<int:id>")
@jwt_required()
def eliminar_persona(id):
    p = Persona.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Persona eliminada correctamente"}), 200
