"""
Decoradores personalizados para control de acceso
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(fn):
    """
    Decorador que verifica que el usuario tenga rol 'admin'.
    Debe usarse después de @jwt_required()
    
    Uso:
        @blueprint.post("/ruta")
        @jwt_required()
        @admin_required
        def mi_funcion():
            # Solo admins pueden acceder aquí
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('rol') != 'admin':
            return jsonify({
                "error": "Acceso denegado",
                "message": "Esta acción requiere privilegios de administrador"
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def mismo_usuario_o_admin(fn):
    """
    Decorador que permite acceso si el usuario es admin O si es el mismo usuario.
    Útil para rutas como ver/editar perfil.
    
    La función decorada debe recibir 'user_id' como parámetro.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_id = kwargs.get('user_id') or kwargs.get('id')
        
        es_admin = claims.get('rol') == 'admin'
        es_mismo_usuario = claims.get('sub') == user_id
        
        if not (es_admin or es_mismo_usuario):
            return jsonify({
                "error": "Acceso denegado",
                "message": "Solo puedes acceder a tu propia información"
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper