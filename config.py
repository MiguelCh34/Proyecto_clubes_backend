import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:Adilion2002_@localhost:5432/proyecto_clubes"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seguridad JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_dev")
