from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, Categoria  # ← Cambiado

categoria_bp = Blueprint("categoria_bp", __name__)


# ================================
#  LISTAR CATEGORÍAS
# ================================
@categoria_bp.get("/listar_categorias")
@jwt_required(optional=True)  # ← IMPORTANTE: optional=True para permitir sin token en desarrollo
def listar_categorias():
    """
    Lista todas las categorías.
    NOTA: Tu tabla se llama 'categoria' y el modelo es 'Categoria'
    Campos: ID_Categoria, Nombre_Categoria
    """
    categorias = Categoria.query.all()
    return jsonify([
        {
            "ID_Categoria": c.ID_Categoria,
            "Nombre": c.Nombre_Categoria,
            "Descripcion": None  # Tu tabla no tiene descripción
        }
        for c in categorias
    ]), 200


# ================================
#  CREAR CATEGORÍA
# ================================
@categoria_bp.post("/crear_categoria")
@jwt_required()
@admin_required
def crear_categoria():
    data = request.get_json() or {}
    nombre = data.get("Nombre") or data.get("Nombre_Categoria")

    if not nombre:
        return jsonify({"error": "Nombre es obligatorio"}), 400

    if Categoria.query.filter_by(Nombre_Categoria=nombre).first():
        return jsonify({"error": "La categoría ya existe"}), 400

    nueva = Categoria(Nombre_Categoria=nombre)
    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        "message": "Categoría creada correctamente",
        "ID_Categoria": nueva.ID_Categoria
    }), 201


# ================================
#  ACTUALIZAR CATEGORÍA
# ================================
@categoria_bp.put("/actualizar_categoria/<int:id>")
@jwt_required()
@admin_required
def actualizar_categoria(id):
    c = Categoria.query.filter_by(ID_Categoria=id).first_or_404()
    data = request.get_json() or {}

    if "Nombre" in data or "Nombre_Categoria" in data:
        nuevo = data.get("Nombre") or data.get("Nombre_Categoria")

        # Validar duplicado
        if Categoria.query.filter(
            Categoria.Nombre_Categoria == nuevo,
            Categoria.ID_Categoria != id
        ).first():
            return jsonify({"error": "Ese nombre ya está en uso"}), 400

        c.Nombre_Categoria = nuevo

    db.session.commit()
    return jsonify({"message": "Categoría actualizada correctamente"}), 200


# ================================
#  ELIMINAR CATEGORÍA
# ================================
@categoria_bp.delete("/eliminar_categoria/<int:id>")
@jwt_required()
@admin_required
def eliminar_categoria(id):
    c = Categoria.query.filter_by(ID_Categoria=id).first_or_404()
    db.session.delete(c)
    db.session.commit()

    return jsonify({"message": "Categoría eliminada exitosamente"}), 200