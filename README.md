# 🚀 UniClubs Backend - API REST

Backend del sistema de gestión de clubes universitarios. API REST construida con Flask y desplegada en Render.

---

## 🌐 Producción

**URL de la API:** https://uniclubs-backend.onrender.com

**Estado:** ✅ En producción

**Plataforma:** Render (Free Tier)

**Base de datos:** Neon PostgreSQL (Serverless)

---

## 📋 Tabla de Contenidos

- [Tecnologías](#-tecnologías)
- [Arquitectura](#-arquitectura)
- [Endpoints Principales](#-endpoints-principales)
- [Instalación Local](#-instalación-local)
- [Variables de Entorno](#-variables-de-entorno)
- [Deployment en Render](#-deployment-en-render)
- [Base de Datos](#-base-de-datos)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🛠️ Tecnologías

- **Python** 3.13
- **Flask** 3.1.2 - Framework web
- **Gunicorn** 21.2.0 - Servidor WSGI
- **SQLAlchemy** 2.0.44 - ORM
- **PostgreSQL** 15 - Base de datos
- **Flask-JWT-Extended** 4.7.1 - Autenticación JWT
- **Flask-CORS** 4.0.0 - Cross-Origin Resource Sharing
- **Flask-Migrate** 4.1.0 - Migraciones de base de datos

---

## 🏗️ Arquitectura

```
Internet
   ↓
Render Load Balancer
   ↓
Gunicorn (4 workers)
   ↓
Flask Application
   ↓
SQLAlchemy ORM
   ↓
Neon PostgreSQL (Cloud)
```

---

## 📡 Endpoints Principales

### Autenticación

```http
POST   /auth/register          # Registro de usuarios
POST   /auth/login             # Inicio de sesión
POST   /auth/refresh           # Renovar token
GET    /auth/me                # Info del usuario actual (protegido)
```

### Clubes

```http
GET    /club/listar_clubes     # Listar todos los clubes
GET    /club/:id               # Obtener club por ID
POST   /club/crear_club        # Crear club (admin)
PUT    /club/actualizar_club/:id  # Actualizar club (admin)
DELETE /club/eliminar_club/:id   # Eliminar club (admin)
```

### Actividades

```http
GET    /actividad/listar_actividades  # Listar actividades
POST   /actividad/crear_actividad     # Crear actividad (protegido)
PUT    /actividad/actualizar/:id      # Actualizar actividad
DELETE /actividad/eliminar/:id        # Eliminar actividad
```

### Inscripciones

```http
GET    /inscripcion/listar     # Listar inscripciones
POST   /inscripcion/inscribir  # Inscribirse a un club (protegido)
DELETE /inscripcion/eliminar/:id  # Desinscribirse
```

**Documentación completa:** Ver colección de Postman o código fuente

---

## 💻 Instalación Local

### Requisitos

- Python 3.10+
- PostgreSQL 15+
- Git

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/MiguelCh34/Proyecto_clubes_backend.git
cd Proyecto_clubes_backend

# 2. Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Crear base de datos
flask db upgrade

# 6. Ejecutar
flask run
# O en producción:
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

La API estará disponible en: http://localhost:5000

---

## 🔐 Variables de Entorno

### Desarrollo (.env)

```env
FLASK_APP=app.py
FLASK_ENV=development

# Base de datos local
DATABASE_URL=postgresql://user:password@localhost:5432/uniclubs_db

# Seguridad
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Producción (Render)

En Render → Settings → Environment Variables:

```env
DATABASE_URL=postgresql://neondb_owner:***@ep-fragrant-butterfly-***.us-east-2.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=production-secret-key
JWT_SECRET_KEY=production-jwt-secret-key
FLASK_ENV=production
CORS_ORIGINS=https://proyecto-clubes-web-ii.vercel.app
```

---

## 🚀 Deployment en Render

### Configuración del Servicio

1. **Crear Web Service** en Render
2. **Conectar repositorio:** `Proyecto_clubes_backend`
3. **Configuración:**
   ```
   Name: uniclubs-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (vacío)
   Runtime: Python 3
   ```

4. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Start Command:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
   ```

6. **Variables de entorno:** (ver sección anterior)

### Auto-Deploy

- ✅ Activado
- Cada push a `main` despliega automáticamente
- Tiempo de deploy: ~2-3 minutos

### Health Checks

Render verifica que el servicio responda en el puerto especificado.

---

## 🗄️ Base de Datos

### Neon PostgreSQL

**Características:**
- Serverless PostgreSQL
- Auto-suspend después de 5 min de inactividad
- SSL requerido
- Región: US East (Ohio)

**Conexión:**
```
Host: ep-fragrant-butterfly-a6c8nqnv.us-east-2.aws.neon.tech
Port: 5432
Database: neondb
User: neondb_owner
SSL Mode: require
```

### Esquema

**11 tablas principales:**
- `usuario` - Usuarios del sistema
- `persona` - Información personal
- `club` - Clubes universitarios
- `actividad` - Actividades de clubes
- `inscripcion` - Relación usuario-club
- `roles` - Roles de participación
- `estado` - Estados de entidades
- `sede` - Sedes universitarias
- `facultad` - Facultades
- `categoria` - Categorías de clubes
- `actividades_realizadas` - Participación en actividades

### Migraciones

```bash
# Crear migración
flask db migrate -m "descripción"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade
```

---

## 📁 Estructura del Proyecto

```
Proyecto_clubes_backend/
├── app.py                 # Aplicación Flask principal
├── wsgi.py               # Punto de entrada WSGI para Gunicorn
├── config.py             # Configuración de la aplicación
├── requirements.txt      # Dependencias Python
├── .env.example          # Template de variables de entorno
├── .gitignore            # Archivos ignorados por Git
│
├── database/
│   └── models.py         # Modelos SQLAlchemy (11 tablas)
│
├── routes/               # Blueprints de rutas
│   ├── auth_routes.py    # Autenticación (login, register)
│   ├── club_routes.py    # CRUD de clubes
│   ├── actividad_routes.py  # CRUD de actividades
│   ├── persona_routes.py    # CRUD de personas
│   ├── inscripcion_routes.py  # Inscripciones
│   ├── estado_routes.py
│   ├── rol_routes.py
│   ├── facultad_routes.py
│   ├── sede_routes.py
│   ├── categoria_routes.py
│   └── participacion_routes.py
│
├── services/             # Lógica de negocio
│   └── usuario_service.py
│
└── utils/                # Utilidades
    └── decorators.py     # Decoradores personalizados (@admin_required)
```

---

## 🔒 Seguridad

### Autenticación JWT

- Tokens firmados con `JWT_SECRET_KEY`
- Access token: válido por 1 hora
- Refresh token: válido por 30 días
- Tokens incluyen: user_id, email, nombre, rol

### Autorización

```python
# Decoradores disponibles
@jwt_required()          # Usuario autenticado
@admin_required          # Solo administradores
```

### Hashing de Contraseñas

- Algoritmo: Werkzeug Security (scrypt)
- Las contraseñas nunca se almacenan en texto plano

### CORS

Configurado para aceptar peticiones solo desde:
- Frontend en Vercel (producción)
- localhost:3000 (desarrollo)

---

## 🐛 Debugging

### Ver logs en Render

```
Render Dashboard → uniclubs-backend → Logs
```

### Logs locales

```bash
# Con Flask
flask run

# Con Gunicorn (como producción)
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - wsgi:app
```

---

## 🧪 Testing

```bash
# Ejecutar tests (si existen)
pytest

# Con coverage
pytest --cov=app
```

---

## 📚 Recursos Adicionales

- **Frontend:** https://github.com/MiguelCh34/Proyecto_clubes_frontend
- **Docker Setup:** https://github.com/MiguelCh34/Proyecto_clubes_docker
- **Flask Docs:** https://flask.palletsprojects.com/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Render Docs:** https://render.com/docs

---

## 👨‍💻 Autor

**Miguel Chiriboga**
- GitHub: [@MiguelCh34](https://github.com/MiguelCh34)
- Email: miguelchiriboga2002@hotmail.com

---

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

---

## 🆘 Soporte

Si encuentras algún problema:

1. Revisa los logs en Render
2. Verifica las variables de entorno
3. Consulta la documentación
4. Abre un issue en GitHub

---

**API Status:** ✅ Online at https://uniclubs-backend.onrender.com