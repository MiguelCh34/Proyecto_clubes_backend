from flask import Blueprint, request, jsonify
from .. import db   # IMPORTACIÓN CORRECTA DESDE EL PAQUETE
from ..utils.jwt_middleware import jwt_required


def create_crud(model, model_name):
    # 👇 NOMBRE ÚNICO PARA EVITAR CONFLICTOS
    bp = Blueprint(f"{model_name.lower()}_crud", __name__)

    # ========== LISTAR ==========
    @bp.route("/", methods=["GET"])
    @jwt_required
    def get_all():
        items = model.query.all()
        return jsonify([item_to_dict(i) for i in items])

    # ========== OBTENER POR ID ==========
    @bp.route("/<int:item_id>", methods=["GET"])
    @jwt_required
    def get_by_id(item_id):
        item = model.query.get_or_404(item_id)
        return jsonify(item_to_dict(item))

    # ========== CREAR ==========
    @bp.route("/", methods=["POST"])
    @jwt_required
    def create():
        data = request.get_json()
        item = model(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify(item_to_dict(item)), 201

    # ========== ACTUALIZAR ==========
    @bp.route("/<int:item_id>", methods=["PUT"])
    @jwt_required
    def update(item_id):
        item = model.query.get_or_404(item_id)
        data = request.get_json()

        for key, value in data.items():
            setattr(item, key, value)

        db.session.commit()
        return jsonify(item_to_dict(item))

    # ========== ELIMINAR ==========
    @bp.route("/<int:item_id>", methods=["DELETE"])
    @jwt_required
    def delete(item_id):
        item = model.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": f"{model_name} eliminado"})

    return bp


# Convierte modelo → dict
def item_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
