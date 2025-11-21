from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db


# ============================================================
#                       TABLA: SEDE
# ============================================================

class Sede(db.Model):
    __tablename__ = "sede"

    ID_Sede = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Ubicacion = db.Column(db.String(200), nullable=False)

    clubes = db.relationship("Club", back_populates="sede")


# ============================================================
#                       TABLA: CATEGORIA
# ============================================================

class Categoria(db.Model):
    __tablename__ = "categoria"

    ID_Categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Categoria = db.Column(db.String(100), nullable=False, unique=True)


# ============================================================
#                       TABLA: ESTADO
# ============================================================

class Estado(db.Model):
    __tablename__ = "estado"

    ID_Estado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_estado = db.Column(db.String(50), nullable=False, unique=True)

    clubes = db.relationship("Club", back_populates="estado")
    personas = db.relationship("Persona", back_populates="estado")
    actividades = db.relationship("Actividad", back_populates="estado")
    inscripciones = db.relationship("Inscripcion", back_populates="estado")
    participaciones = db.relationship("ActividadesRealizadas", back_populates="estado")


# ============================================================
#                       TABLA: ROLES
# ============================================================

class Roles(db.Model):
    __tablename__ = "roles"

    ID_Roles = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_Rol = db.Column(db.String(50), nullable=False, unique=True)

    inscripciones = db.relationship("Inscripcion", back_populates="rol")
    participaciones = db.relationship("ActividadesRealizadas", back_populates="rol")


# ============================================================
#                       TABLA: USUARIO
# ============================================================

class Usuario(db.Model):
    __tablename__ = "usuario"

    ID_Usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    clubes = db.relationship("Club", back_populates="usuario")
    personas = db.relationship("Persona", back_populates="usuario")
    actividades = db.relationship("Actividad", back_populates="usuario")
    inscripciones = db.relationship("Inscripcion", back_populates="usuario")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ============================================================
#                       TABLA: FACULTAD
# ============================================================

class Facultad(db.Model):
    __tablename__ = "facultad"

    ID_Facultad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(150), nullable=False)

    clubes = db.relationship("Club", back_populates="facultad")


# ============================================================
#                       TABLA: CLUB
# ============================================================

class Club(db.Model):
    __tablename__ = "club"

    ID_Club = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(150), nullable=False)
    Descripcion = db.Column(db.Text)
    Tipo = db.Column(db.String(100))
    Duracion = db.Column(db.String(50))

    ID_Sede = db.Column(db.Integer, db.ForeignKey("sede.ID_Sede"), nullable=False)
    ID_Facultad = db.Column(db.Integer, db.ForeignKey("facultad.ID_Facultad"))
    ID_Estado = db.Column(db.Integer, db.ForeignKey("estado.ID_Estado"), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.ID_Usuario"), nullable=False)

    sede = db.relationship("Sede", back_populates="clubes")
    facultad = db.relationship("Facultad", back_populates="clubes")
    estado = db.relationship("Estado", back_populates="clubes")
    usuario = db.relationship("Usuario", back_populates="clubes")

    actividades = db.relationship("Actividad", back_populates="club")
    inscripciones = db.relationship("Inscripcion", back_populates="club")


# ============================================================
#                       TABLA: PERSONA
# ============================================================

class Persona(db.Model):
    __tablename__ = "persona"

    ID_Persona = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Apellido = db.Column(db.String(100), nullable=False)
    Carrera = db.Column(db.String(150))
    Correo_institucional = db.Column(db.String(150), unique=True)
    Cantidad = db.Column(db.Integer, default=1)
    Edad = db.Column(db.Integer)
    Cedula = db.Column(db.String(20), unique=True)
    Telefono = db.Column(db.String(20))

    ID_Estado = db.Column(db.Integer, db.ForeignKey("estado.ID_Estado"), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.ID_Usuario"), nullable=False)

    estado = db.relationship("Estado", back_populates="personas")
    usuario = db.relationship("Usuario", back_populates="personas")

    inscripciones = db.relationship("Inscripcion", back_populates="persona")
    participaciones = db.relationship("ActividadesRealizadas", back_populates="estudiante")


# ============================================================
#                       TABLA: ACTIVIDAD
# ============================================================

class Actividad(db.Model):
    __tablename__ = "actividad"

    ID_Actividad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(150), nullable=False)
    Descripcion = db.Column(db.Text)
    Fecha = db.Column(db.DateTime, nullable=False)
    Lugar = db.Column(db.String(200))

    ID_Club = db.Column(db.Integer, db.ForeignKey("club.ID_Club"), nullable=False)
    ID_Estado = db.Column(db.Integer, db.ForeignKey("estado.ID_Estado"), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.ID_Usuario"), nullable=False)

    club = db.relationship("Club", back_populates="actividades")
    estado = db.relationship("Estado", back_populates="actividades")
    usuario = db.relationship("Usuario", back_populates="actividades")

    participaciones = db.relationship("ActividadesRealizadas", back_populates="actividad")


# ============================================================
#                       TABLA: INSCRIPCION
# ============================================================

class Inscripcion(db.Model):
    __tablename__ = "inscripcion"

    ID_Inscripcion = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ID_Persona = db.Column(db.Integer, db.ForeignKey("persona.ID_Persona"), nullable=False)
    ID_Club = db.Column(db.Integer, db.ForeignKey("club.ID_Club"), nullable=False)
    ID_Roles = db.Column(db.Integer, db.ForeignKey("roles.ID_Roles"), nullable=False)
    Fecha_Ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    ID_Estado = db.Column(db.Integer, db.ForeignKey("estado.ID_Estado"), nullable=False)
    ID_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.ID_Usuario"), nullable=False)

    persona = db.relationship("Persona", back_populates="inscripciones")
    club = db.relationship("Club", back_populates="inscripciones")
    rol = db.relationship("Roles", back_populates="inscripciones")
    estado = db.relationship("Estado", back_populates="inscripciones")
    usuario = db.relationship("Usuario", back_populates="inscripciones")

    __table_args__ = (
        db.UniqueConstraint("ID_Persona", "ID_Club", name="uq_persona_club"),
    )


# ============================================================
#                 TABLA: ACTIVIDADES REALIZADAS
# ============================================================

class ActividadesRealizadas(db.Model):
    __tablename__ = "actividades_realizadas"

    ID_Participacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Estudiante = db.Column(db.Integer, db.ForeignKey("persona.ID_Persona"), nullable=False)
    ID_Actividad = db.Column(db.Integer, db.ForeignKey("actividad.ID_Actividad"), nullable=False)
    ID_Roles = db.Column(db.Integer, db.ForeignKey("roles.ID_Roles"), nullable=False)
    ID_Estado = db.Column(db.Integer, db.ForeignKey("estado.ID_Estado"), nullable=False)

    estudiante = db.relationship("Persona", back_populates="participaciones")
    actividad = db.relationship("Actividad", back_populates="participaciones")
    rol = db.relationship("Roles", back_populates="participaciones")
    estado = db.relationship("Estado", back_populates="participaciones")

    __table_args__ = (
        db.UniqueConstraint("ID_Estudiante", "ID_Actividad", name="uq_estudiante_actividad"),
    )
