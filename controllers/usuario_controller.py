from flask import Blueprint

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/usuarios')
def get_usuarios():
    return {"message": "Usuarios funcionando"}
