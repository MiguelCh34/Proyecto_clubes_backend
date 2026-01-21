# Usa una imagen base de Python 3.10 o superior
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt y luego instala las dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código completo del backend
COPY . /app/

# Expone el puerto 5000 para Flask
EXPOSE 5000

# Comando para ejecutar la app de Flask
CMD ["flask", "run", "--host=0.0.0.0"]