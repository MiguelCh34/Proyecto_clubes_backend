from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Importaciones correctas
from .. import db
from ..database.models import Categoria


categoria_bp = Blueprint("categoria", __name__)   # Nombre interno correcto


# ================================
#  LISTAR CATEGORÍAS
# ================================
@categoria_bp.get("/listar_categoria")
@jwt_required(optional=True)
def listar_categoria():
    categorias = Categoria.query.all()

    return jsonify([
        {
            "ID_Categoria": c.ID_Categoria,
            "Nombre_Categoria": c.Nombre_Categoria
        } for c in categorias
    ]), 200


# ================================
#  CREAR CATEGORÍA
# ================================
@categoria_bp.post("/crear_categoria")
@jwt_required()
def crear_categoria():
    data = request.get_json() or {}

    nombre = data.get("Nombre_Categoria")

    if not nombre:
        return jsonify({"error": "Nombre_Categoria es obligatorio"}), 400

    if Categoria.query.filter_by(Nombre_Categoria=nombre).first():
        return jsonify({"error": "La categoría ya existe"}), 409

    nueva_categoria = Categoria(Nombre_Categoria=nombre)
    db.session.add(nueva_categoria)
    db.session.commit()

    return jsonify({
        "message": "Categoría creada exitosamente",
        "ID_Categoria": nueva_categoria.ID_Categoria
    }), 201


# ================================
#  OBTENER CATEGORÍA POR ID
# ================================
@categoria_bp.get("/obtener_categoria/<int:id>")
@jwt_required(optional=True)
def obtener_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    return jsonify({
        "ID_Categoria": categoria.ID_Categoria,
        "Nombre_Categoria": categoria.Nombre_Categoria
    }), 200


# ================================
#  ACTUALIZAR CATEGORÍA
# ================================
@categoria_bp.put("/actualizar_categoria/<int:id>")
@jwt_required()
def actualizar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    data = request.get_json() or {}

    nuevo_nombre = data.get("Nombre_Categoria")

    if nuevo_nombre:
        existe = Categoria.query.filter(
            Categoria.Nombre_Categoria == nuevo_nombre,
            Categoria.ID_Categoria != id
        ).first()

        if existe:
            return jsonify({"error": "Ya existe una categoría con ese nombre"}), 409

        categoria.Nombre_Categoria = nuevo_nombre

    db.session.commit()

    return jsonify({"message": "Categoría actualizada correctamente"}), 200


# ================================
#  ELIMINAR CATEGORÍA
# ================================
@categoria_bp.delete("/eliminar_categoria/<int:id>")
@jwt_required()
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    db.session.delete(categoria)
    db.session.commit()

    return jsonify({"message": "Categoría eliminada"}), 200
