FROM python:3.12-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema necesarias para psycopg2 y pipenv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
    && pip install --upgrade pip \
    && pip install pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio del app dentro del contenedor
WORKDIR /app

# Copiar Pipenv y Pipenv.lock primero para aprovechar cache
COPY Pipfile Pipfile.lock /app/

# Instalar dependencias del proyecto con pipenv sin virtualenv
RUN pipenv install --system --deploy

# Copiar el resto del proyecto
COPY . /app

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
