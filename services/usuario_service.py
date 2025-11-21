# backend_clubes/services/usuario_service.py
from .. import db
from ..database.models import Usuario

def listar_usuarios():
    return Usuario.query.all()

def obtener_usuario(id_usuario: int):
    return Usuario.query.get_or_404(id_usuario)

def actualizar_usuario(u: Usuario, data: dict):
    if "nombre" in data:
        u.nombre = data["nombre"]
    if "email" in data:
        from sqlalchemy import and_
        existe = Usuario.query.filter(
            and_(Usuario.email == data["email"], Usuario.ID_Usuario != u.ID_Usuario)
        ).first()
        if existe:
            return "Email en uso"
        u.email = data["email"]
    if "password" in data:
        u.set_password(data["password"])
    db.session.commit()
    return None  # sin error
