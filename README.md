# Backend - Sistema de Gestión de Clubes (Flask)

Este backend forma parte del avance del proyecto y permite gestionar entidades como usuarios, clubes, categorías, actividades, inscripciones y más.  

El sistema utiliza autenticación con **JWT** para proteger rutas y separar accesos.

---

## 🚀 Tecnologías utilizadas

- Python 3
- Flask
- Flask-JWT-Extended
- SQLAlchemy
- Flask-Migrate (Migraciones)
- Postman (Pruebas)
- PostgreSQL / MySQL / SQLite (según configuración)

---

## 🔑 Configuración del entorno
1. Activar entorno virtual:

venv\Scripts\activate


2. Instalar dependencias:

pip install -r requirements.txt


3. Configurar archivo `.env`:

JWT_SECRET_KEY=secretkey123
DATABASE_URL=sqlite:///clubes.db

## ▶️ Ejecutar el servidor

python -m backend_clubes.app


El backend correrá en: http://127.0.0.1:5000/

## 🔐 Autenticación

Solo algunas rutas son públicas.  
Para acceder a rutas protegidas, se debe iniciar sesión:

POST → `/auth/login`

El backend responde con un:

```json
{
  "access_token": "xxxxxx"
}

Este token debe enviarse luego en el header:

Authorization: Bearer TOKEN_AQUI

 


