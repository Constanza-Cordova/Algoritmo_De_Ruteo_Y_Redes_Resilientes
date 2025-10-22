# etl/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los scripts ETL y loaders
COPY *.py ./

# Crear directorio de salida
RUN mkdir -p /app/out

# Variables de entorno por defecto
ENV OUT_DIR=/app/out
ENV WEB_DATA_DIR=/webdata
ENV PYTHONUNBUFFERED=1

# Script de entrada
CMD ["python", "run_etl.py"]
