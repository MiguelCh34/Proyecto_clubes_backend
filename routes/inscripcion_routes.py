from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, Inscripcion, Persona, Club, Roles, Estado, Usuario  # ← Cambiado

inscripcion_bp = Blueprint("inscripcion_bp", __name__)


# ================================
#  LISTAR INSCRIPCIONES
# ================================
@inscripcion_bp.get("/listar_inscripciones")
@jwt_required(optional=True)
def listar_inscripciones():
    inscripciones = Inscripcion.query.all()
    return jsonify([
        {
            "ID_Inscripcion": i.ID_Inscripcion,
            "ID_Persona": i.ID_Persona,
            "ID_Club": i.ID_Club,
            "Fecha_Ingreso": i.Fecha_Ingreso.isoformat() if i.Fecha_Ingreso else None
        }
        for i in inscripciones
    ]), 200


# ================================
#  LISTAR INSCRITOS DE UN CLUB (ADMIN)
# ================================
@inscripcion_bp.get("/club/<int:club_id>/inscritos")
@jwt_required()
@admin_required
def listar_inscritos_club(club_id):
    """Ver todos los inscritos (activos e inactivos) en un club específico"""
    inscripciones = db.session.query(
        Inscripcion.ID_Inscripcion,
        Persona.Nombre,
        Persona.Apellido,
        Persona.Correo_institucional,
        Persona.Carrera,
        Roles.Nombre_Rol,
        Inscripcion.Fecha_Ingreso,
        Estado.Nombre_estado
    ).select_from(Inscripcion)\
     .join(Persona, Inscripcion.ID_Persona == Persona.ID_Persona)\
     .join(Roles, Inscripcion.ID_Roles == Roles.ID_Roles)\
     .join(Estado, Inscripcion.ID_Estado == Estado.ID_Estado)\
     .filter(Inscripcion.ID_Club == club_id)\
     .order_by(Estado.Nombre_estado.desc(), Inscripcion.Fecha_Ingreso.desc())\
     .all()

    # Separar activos e inactivos
    activos = []
    inactivos = []
    
    for i in inscripciones:
        dato = {
            "ID_Inscripcion": i[0],
            "Nombre_Completo": f"{i[1]} {i[2]}",
            "Correo": i[3],
            "Carrera": i[4] or 'N/A',
            "Rol": i[5],
            "Fecha_Ingreso": i[6].isoformat() if i[6] else None,
            "Estado": i[7]
        }
        
        if i[7].lower() == 'activo':
            activos.append(dato)
        else:
            inactivos.append(dato)

    return jsonify({
        "activos": activos,
        "inactivos": inactivos
    }), 200


# ================================
#  INSCRIBIRSE A UN CLUB (USUARIO)
# ================================
@inscripcion_bp.post("/inscribirse/<int:club_id>")
@jwt_required()
def inscribirse_club(club_id):
    """Permite a un usuario inscribirse en un club"""
    current_user_id = get_jwt_identity()
    
    # Verificar que el club existe
    club = Club.query.get(club_id)
    if not club:
        return jsonify({"error": "El club no existe"}), 404

    # Buscar la persona asociada al usuario actual
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"error": "No se encontró un perfil de persona asociado a tu usuario. Por favor contacta al administrador."}), 404

    # Verificar si ya está inscrito (activo o inactivo)
    inscripcion_existente = Inscripcion.query.filter_by(
        ID_Persona=persona.ID_Persona,
        ID_Club=club_id
    ).first()

    # Obtener estado activo
    estado_activo = Estado.query.filter_by(Nombre_estado="Activo").first()
    if not estado_activo:
        estado_activo = Estado.query.first()

    if inscripcion_existente:
        # Si existe pero está inactiva, reactivarla
        if inscripcion_existente.ID_Estado != estado_activo.ID_Estado:
            inscripcion_existente.ID_Estado = estado_activo.ID_Estado
            inscripcion_existente.Fecha_Ingreso = datetime.utcnow()
            db.session.commit()
            return jsonify({"message": "Te has reinscrito exitosamente al club"}), 200
        else:
            return jsonify({"error": "Ya estás inscrito en este club"}), 400

    # Obtener rol de "Miembro"
    rol_miembro = Roles.query.filter_by(Nombre_Rol="Miembro").first()
    if not rol_miembro:
        rol_miembro = Roles.query.first()

    # Crear inscripción
    nueva_inscripcion = Inscripcion(
        ID_Persona=persona.ID_Persona,
        ID_Club=club_id,
        ID_Roles=rol_miembro.ID_Roles,
        ID_Estado=estado_activo.ID_Estado,
        ID_Usuario=current_user_id,
        Fecha_Ingreso=datetime.utcnow()
    )

    db.session.add(nueva_inscripcion)
    db.session.commit()

    return jsonify({
        "message": "Te has inscrito exitosamente al club",
        "ID_Inscripcion": nueva_inscripcion.ID_Inscripcion
    }), 201


# ================================
#  CANCELAR INSCRIPCIÓN (USUARIO)
# ================================
@inscripcion_bp.delete("/cancelar_inscripcion/<int:club_id>")
@jwt_required()
def cancelar_inscripcion(club_id):
    """Permite a un usuario cancelar su inscripción en un club"""
    current_user_id = get_jwt_identity()
    
    # Buscar la persona asociada al usuario actual
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"error": "No se encontró tu perfil"}), 404

    # Buscar la inscripción
    inscripcion = Inscripcion.query.filter_by(
        ID_Persona=persona.ID_Persona,
        ID_Club=club_id
    ).first()

    if not inscripcion:
        return jsonify({"error": "No estás inscrito en este club"}), 404

    # En lugar de eliminar, cambiar estado a "Inactivo"
    estado_inactivo = Estado.query.filter_by(Nombre_estado="Inactivo").first()
    if estado_inactivo:
        inscripcion.ID_Estado = estado_inactivo.ID_Estado
        db.session.commit()
        return jsonify({"message": "Inscripción cancelada exitosamente"}), 200
    else:
        # Si no existe estado Inactivo, eliminar (comportamiento anterior)
        db.session.delete(inscripcion)
        db.session.commit()
        return jsonify({"message": "Inscripción cancelada exitosamente"}), 200


# ================================
#  VERIFICAR SI ESTÁ INSCRITO
# ================================
@inscripcion_bp.get("/verificar_inscripcion/<int:club_id>")
@jwt_required()
def verificar_inscripcion(club_id):
    """Verifica si el usuario actual está inscrito en un club"""
    current_user_id = get_jwt_identity()
    
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"inscrito": False}), 200

    # Buscar inscripción ACTIVA
    estado_activo = Estado.query.filter_by(Nombre_estado="Activo").first()
    
    inscripcion = Inscripcion.query.filter_by(
        ID_Persona=persona.ID_Persona,
        ID_Club=club_id,
        ID_Estado=estado_activo.ID_Estado if estado_activo else None
    ).first()

    return jsonify({
        "inscrito": inscripcion is not None,
        "ID_Inscripcion": inscripcion.ID_Inscripcion if inscripcion else None
    }), 200


# ================================
#  MIS INSCRIPCIONES (USUARIO)
# ================================
@inscripcion_bp.get("/mis_inscripciones")
@jwt_required()
def mis_inscripciones():
    """Obtiene todos los clubes ACTIVOS a los que el usuario está inscrito"""
    current_user_id = get_jwt_identity()
    
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify([]), 200

    # Obtener estado activo
    estado_activo = Estado.query.filter_by(Nombre_estado="Activo").first()
    
    inscripciones = db.session.query(
        Club.ID_Club,
        Club.Nombre,
        Club.Descripcion,
        Inscripcion.Fecha_Ingreso,
        Roles.Nombre_Rol,
        Estado.Nombre_estado
    ).select_from(Inscripcion)\
     .join(Club, Inscripcion.ID_Club == Club.ID_Club)\
     .join(Roles, Inscripcion.ID_Roles == Roles.ID_Roles)\
     .join(Estado, Inscripcion.ID_Estado == Estado.ID_Estado)\
     .filter(
         Inscripcion.ID_Persona == persona.ID_Persona,
         Inscripcion.ID_Estado == estado_activo.ID_Estado  # ← SOLO ACTIVAS
     ).all()

    return jsonify([
        {
            "ID_Club": i[0],
            "Nombre_Club": i[1],
            "Descripcion": i[2],
            "Fecha_Ingreso": i[3].isoformat() if i[3] else None,
            "Rol": i[4],
            "Estado": i[5]
        }
        for i in inscripciones
    ]), 200


# ================================
#  CREAR INSCRIPCIÓN (ADMIN)
# ================================
@inscripcion_bp.post("/crear_inscripcion")
@jwt_required()
@admin_required
def crear_inscripcion():
    data = request.get_json() or {}

    required = ["ID_Persona", "ID_Club", "ID_Roles", "ID_Estado", "ID_Usuario"]

    if not all(k in data for k in required):
        return jsonify({"error": "Faltan campos obligatorios: ID_Persona, ID_Club, ID_Roles, ID_Estado, ID_Usuario"}), 400

    # Validación existencias
    if not Persona.query.get(data["ID_Persona"]):
        return jsonify({"error": "La persona no existe"}), 400

    if not Club.query.get(data["ID_Club"]):
        return jsonify({"error": "El club no existe"}), 400

    if not Roles.query.get(data["ID_Roles"]):
        return jsonify({"error": "El rol no existe"}), 400

    if not Estado.query.get(data["ID_Estado"]):
        return jsonify({"error": "El estado no existe"}), 400

    if not Usuario.query.get(data["ID_Usuario"]):
        return jsonify({"error": "El usuario no existe"}), 400

    # Validación única (bool prevent)
    if Inscripcion.query.filter_by(ID_Persona=data["ID_Persona"], ID_Club=data["ID_Club"]).first():
        return jsonify({"error": "Esa persona ya está inscrita en ese club"}), 400

    insc = Inscripcion(
        ID_Persona=data["ID_Persona"],
        ID_Club=data["ID_Club"],
        ID_Roles=data["ID_Roles"],
        ID_Estado=data["ID_Estado"],
        ID_Usuario=data["ID_Usuario"],
        Fecha_Ingreso=datetime.utcnow()
    )

    db.session.add(insc)
    db.session.commit()

    return jsonify({"message": "Inscripción creada correctamente", "ID_Inscripcion": insc.ID_Inscripcion}), 201


# ================================
#  OBTENER UNA INSCRIPCIÓN
# ================================
@inscripcion_bp.get("/obtener_inscripcion/<int:id>")
@jwt_required(optional=True)
def obtener_inscripcion(id):
    i = Inscripcion.query.get_or_404(id)
    return jsonify({
        "ID_Inscripcion": i.ID_Inscripcion,
        "ID_Persona": i.ID_Persona,
        "ID_Club": i.ID_Club,
        "ID_Roles": i.ID_Roles,
        "ID_Estado": i.ID_Estado,
        "ID_Usuario": i.ID_Usuario,
        "Fecha_Ingreso": i.Fecha_Ingreso.isoformat() if i.Fecha_Ingreso else None
    }), 200


# ================================
#  ACTUALIZAR INSCRIPCIÓN
# ================================
@inscripcion_bp.put("/actualizar_inscripcion/<int:id>")
@jwt_required()
@admin_required
def actualizar_inscripcion(id):
    insc = Inscripcion.query.get_or_404(id)
    data = request.get_json() or {}

    for field in ["ID_Persona", "ID_Club", "ID_Roles", "ID_Estado", "ID_Usuario"]:
        if field in data:
            setattr(insc, field, data[field])

    db.session.commit()

    return jsonify({"message": "Inscripción actualizada correctamente"}), 200


# ================================
#  ELIMINAR INSCRIPCIÓN (ADMIN)
# ================================
@inscripcion_bp.delete("/eliminar_inscripcion/<int:id>")
@jwt_required()
@admin_required
def eliminar_inscripcion(id):
    insc = Inscripcion.query.get_or_404(id)
    db.session.delete(insc)
    db.session.commit()

    return jsonify({"message": "Inscripción eliminada exitosamente"}), 200