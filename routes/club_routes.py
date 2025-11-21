from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .. import db
from ..database.models import Club, Sede, Facultad, Estado, Usuario

club_bp = Blueprint("club_bp", __name__)


@club_bp.get("/listar_clubes")
@jwt_required()
def listar_clubes():
    clubes = Club.query.all()
    return jsonify([
        {
            "ID_Club": club.ID_Club,
            "Nombre": club.Nombre,
            "Descripcion": club.Descripcion,
            "Tipo": club.Tipo,
            "Duracion": club.Duracion,
            "ID_Sede": club.ID_Sede,
            "ID_Facultad": club.ID_Facultad,
            "ID_Estado": club.ID_Estado,
            "ID_Usuario": club.ID_Usuario
        } for club in clubes
    ]), 200


@club_bp.get("/listar_detalles")
@jwt_required()
def listar_detalles_club():
    resultados = db.session.query(
        Club.ID_Club,
        Club.Nombre,
        Sede.Ubicacion,
        Facultad.Nombre,
        Estado.Nombre_estado
    ).join(Sede).join(Facultad).join(Estado).all()

    return jsonify([
        {
            "ID_Club": r[0],
            "Nombre": r[1],
            "Sede": r[2],
            "Facultad": r[3],
            "Estado": r[4]
        } for r in resultados
    ]), 200


@club_bp.post("/crear_club")
@jwt_required()
def crear_club():
    data = request.get_json()
    nuevo_club = Club(**data)
    db.session.add(nuevo_club)
    db.session.commit()
    return jsonify({"message": "Club creado exitosamente"}), 201


@club_bp.get("/obtener_club/<int:id>")
@jwt_required()
def obtener_club(id):
    club = Club.query.get(id)
    if not club:
        return jsonify({"error": "Club no encontrado"}), 404
    return jsonify({
        "ID_Club": club.ID_Club,
        "Nombre": club.Nombre,
        "Descripcion": club.Descripcion,
        "Tipo": club.Tipo,
        "Duracion": club.Duracion,
        "ID_Sede": club.ID_Sede,
        "ID_Facultad": club.ID_Facultad,
        "ID_Estado": club.ID_Estado,
        "ID_Usuario": club.ID_Usuario
    }), 200


@club_bp.put("/actualizar_club/<int:id>")
@jwt_required()
def actualizar_club(id):
    club = Club.query.get(id)
    if not club:
        return jsonify({"error": "Club no encontrado"}), 404

    data = request.get_json()
    for key, value in data.items():
        setattr(club, key, value)

    db.session.commit()
    return jsonify({"message": "Club actualizado correctamente"}), 200


@club_bp.delete("/eliminar_club/<int:id>")
@jwt_required()
def eliminar_club(id):
    club = Club.query.get(id)
    if not club:
        return jsonify({"error": "Club no encontrado"}), 404

    db.session.delete(club)
    db.session.commit()
    return jsonify({"message": "Club eliminado exitosamente"}), 200
