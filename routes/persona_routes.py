from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import admin_required  # ← Cambiado
from database.models import db, Persona, Estado, Usuario, Roles  # ← Cambiado


persona_bp = Blueprint("persona_bp", __name__)


# ================================
#  LISTAR USUARIOS (NUEVO)
# ================================
@persona_bp.get("/listar_usuarios")
@jwt_required(optional=True)
def listar_usuarios():
    """
    Lista todos los usuarios registrados en la tabla usuario.
    Muestra: nombre, email, rol
    """
    usuarios = Usuario.query.all()
    return jsonify([
        {
            "ID_Usuario": u.ID_Usuario,
            "Nombre": u.nombre,
            "Email": u.email,
            "Rol": u.rol
        }
        for u in usuarios
    ]), 200


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
@admin_required
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
@admin_required
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
@admin_required
def eliminar_persona(id):
    p = Persona.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Persona eliminada correctamente"}), 200


# ================================
#  ASIGNAR ROL ADICIONAL (CORREGIDO)
# ================================
@persona_bp.post("/asignar_rol")
@jwt_required()
@admin_required
def asignar_rol():
    """
    Asigna un rol adicional (Coordinador/Estudiante) a un usuario
    """
    data = request.get_json() or {}
    required = ["ID_Usuario", "Nombre", "Apellido", "Correo_institucional", "ID_Rol", "ID_Estado"]

    if not all(field in data for field in required):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Validar que el usuario existe
    if not Usuario.query.get(data["ID_Usuario"]):
        return jsonify({"error": "El usuario no existe"}), 400

    # ← CORREGIDO: Validar rol usando ID_Roles (no ID_Rol)
    rol_buscado = Roles.query.filter_by(ID_Roles=data["ID_Rol"]).first()
    if not rol_buscado:
        return jsonify({"error": f"El rol con ID {data['ID_Rol']} no existe"}), 400

    # Verificar si ya existe una persona asociada a este usuario
    persona_existente = Persona.query.filter_by(ID_Usuario=data["ID_Usuario"]).first()

    if persona_existente:
        # Actualizar persona existente
        persona_existente.Nombre = data["Nombre"]
        persona_existente.Apellido = data["Apellido"]
        persona_existente.Correo_institucional = data["Correo_institucional"]
        persona_existente.ID_Rol = data["ID_Rol"]
        persona_existente.ID_Estado = data["ID_Estado"]
        
        db.session.commit()
        return jsonify({"message": "Rol actualizado correctamente"}), 200
    else:
        # Crear nueva persona
        nueva_persona = Persona(
            Nombre=data["Nombre"],
            Apellido=data["Apellido"],
            Correo_institucional=data["Correo_institucional"],
            ID_Usuario=data["ID_Usuario"],
            ID_Rol=data["ID_Rol"],
            ID_Estado=data["ID_Estado"]
        )
        
        db.session.add(nueva_persona)
        db.session.commit()
        return jsonify({"message": "Rol asignado correctamente"}), 201


# ================================
#  OBTENER PERFIL ACTUAL
# ================================
@persona_bp.get("/obtener_perfil")
@jwt_required()
def obtener_perfil():
    """Obtiene el perfil del usuario actual"""
    current_user_id = get_jwt_identity()
    
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"error": "No se encontró tu perfil"}), 404
    
    return jsonify({
        "ID_Persona": persona.ID_Persona,
        "Nombre": persona.Nombre,
        "Apellido": persona.Apellido,
        "Correo_institucional": persona.Correo_institucional,
        "Carrera": persona.Carrera,
        "Foto_Perfil": persona.Foto_Perfil
    }), 200


# ================================
#  ACTUALIZAR FOTO DE PERFIL
# ================================
@persona_bp.put("/actualizar_foto_perfil")
@jwt_required()
def actualizar_foto_perfil():
    """Actualiza la URL de la foto de perfil del usuario actual"""
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    if 'foto_perfil' not in data:
        return jsonify({"error": "Falta el campo foto_perfil"}), 400
    
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"error": "No se encontró tu perfil"}), 404
    
    persona.Foto_Perfil = data['foto_perfil']
    db.session.commit()
    
    return jsonify({"message": "Foto de perfil actualizada exitosamente"}), 200


# ================================
#  ACTUALIZAR INFORMACIÓN PERSONAL
# ================================
@persona_bp.put("/actualizar_perfil")
@jwt_required()
def actualizar_perfil():
    """Actualiza la información personal del usuario actual"""
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    
    persona = Persona.query.filter_by(ID_Usuario=current_user_id).first()
    if not persona:
        return jsonify({"error": "No se encontró tu perfil"}), 404
    
    # Actualizar campos permitidos
    if 'Nombre' in data:
        persona.Nombre = data['Nombre']
    if 'Apellido' in data:
        persona.Apellido = data['Apellido']
    if 'Carrera' in data:
        persona.Carrera = data['Carrera']
    if 'Correo_institucional' in data:
        # Verificar que el nuevo correo no esté en uso
        correo_existente = Persona.query.filter(
            Persona.Correo_institucional == data['Correo_institucional'],
            Persona.ID_Persona != persona.ID_Persona
        ).first()
        if correo_existente:
            return jsonify({"error": "Este correo ya está en uso"}), 400
        persona.Correo_institucional = data['Correo_institucional']
    
    db.session.commit()
    
    return jsonify({"message": "Perfil actualizado exitosamente"}), 200