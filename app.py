from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from database.models import db
from config import Config  # ← Cambiado de .config a config

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ========================================
    # CONFIGURACIÓN CORS MÁS PERMISIVA
    # ========================================
    CORS(app)  # Esto permite todo temporalmente

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from database import models  # ← Cambiado de .database a database

    from routes.auth_routes import auth_bp  # ← Removido el punto
    from routes.club_routes import club_bp
    from routes.usuario_routes import usuario_bp
    from routes.actividad_routes import actividad_bp
    from routes.categoria_routes import categoria_bp
    from routes.estado_routes import estado_bp
    from routes.facultad_routes import facultad_bp
    from routes.inscripcion_routes import inscripcion_bp
    from routes.participacion_routes import participacion_bp
    from routes.persona_routes import persona_bp
    from routes.roles_routes import roles_bp
    from routes.sede_routes import sede_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(usuario_bp, url_prefix="/usuarios")
    app.register_blueprint(club_bp, url_prefix="/club")
    app.register_blueprint(actividad_bp, url_prefix="/actividad")
    app.register_blueprint(categoria_bp, url_prefix="/categoria")
    app.register_blueprint(estado_bp, url_prefix="/estado")
    app.register_blueprint(facultad_bp, url_prefix="/facultad")
    app.register_blueprint(inscripcion_bp, url_prefix="/inscripcion")
    app.register_blueprint(participacion_bp, url_prefix="/participacion")
    app.register_blueprint(persona_bp, url_prefix="/persona")
    app.register_blueprint(roles_bp, url_prefix="/rol")
    app.register_blueprint(sede_bp, url_prefix="/sede")

    return app

app = create_app()  # ← Agregado: crear la instancia aquí para que wsgi.py pueda importarla

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)