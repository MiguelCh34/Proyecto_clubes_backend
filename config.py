import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote_plus

load_dotenv(encoding='utf-8')

def test_database_connection(host, user, password, db_name, timeout=3):
    """
    Prueba la conexión a una base de datos PostgreSQL
    Retorna True si la conexión es exitosa, False si falla
    """
    try:
        conn = psycopg2.connect(
            host=host,
            port=5432,
            user=user,
            password=password,
            database=db_name,
            connect_timeout=timeout
        )
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error conectando a {host}: {str(e)}")
        return False

def get_database_uri():
    """
    Intenta conectarse a localhost primero (desarrollo), luego Docker (producción)
    """
    # Configuración desde variables de entorno o valores por defecto
    db_user = os.getenv("DB_USER", "user")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_name = os.getenv("DB_NAME", "club_database")
    
    # Escapar caracteres especiales en la contraseña
    safe_password = quote_plus(db_password)
    
    # Prioridad 1: Intentar conectar a localhost (PostgreSQL local)
    local_host = "localhost"
    print(f"🔍 Intentando conectar a PostgreSQL local ({local_host}:5432)...")
    if test_database_connection(local_host, db_user, db_password, db_name):
        print(f"✅ Conectado a PostgreSQL local ({local_host}:5432)")
        return f"postgresql+psycopg2://{db_user}:{safe_password}@{local_host}:5432/{db_name}"
    
    # Prioridad 2: Intentar conectar a Docker (db:5432)
    docker_host = "db"
    print(f"🔍 Intentando conectar a PostgreSQL en Docker ({docker_host}:5432)...")
    if test_database_connection(docker_host, db_user, db_password, db_name):
        print(f"✅ Conectado a PostgreSQL en Docker ({docker_host}:5432)")
        return f"postgresql+psycopg2://{db_user}:{safe_password}@{docker_host}:5432/{db_name}"
    
    # Prioridad 3: Usar DB_HOST del .env si está definido
    custom_host = os.getenv("DB_HOST")
    if custom_host and custom_host not in ["db", "localhost"]:
        print(f"🔍 Intentando conectar a PostgreSQL personalizado ({custom_host}:5432)...")
        if test_database_connection(custom_host, db_user, db_password, db_name):
            print(f"✅ Conectado a PostgreSQL personalizado ({custom_host}:5432)")
            return f"postgresql+psycopg2://{db_user}:{safe_password}@{custom_host}:5432/{db_name}"
    
    # Fallback
    print("⚠️ No se pudo conectar a ninguna base de datos.")
    print("🔧 Verifica que PostgreSQL esté corriendo.")
    return f"postgresql+psycopg2://{db_user}:{safe_password}@{local_host}:5432/{db_name}"


class Config:
    # Base de datos con detección automática
    # IMPORTANTE: Corregir formato de Neon para SQLAlchemy
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Si la URL viene de Neon y empieza con postgres://, cambiarla a postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        # Si la URL no tiene el driver psycopg2, agregarlo
        if 'postgresql://' in database_url and 'postgresql+psycopg2://' not in database_url:
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback a detección automática local
        SQLALCHEMY_DATABASE_URI = get_database_uri()
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_dev_change_in_production")
    
    # Configuración adicional
    DEBUG = os.getenv("FLASK_ENV") == "development"
    
    # Información de la base de datos (para debug)
    DB_USER = os.getenv("DB_USER", "user")
    DB_NAME = os.getenv("DB_NAME", "club_database")
    DB_HOST = os.getenv("DB_HOST", "auto-detect")