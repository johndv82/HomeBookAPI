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
       bash \
    && pip install --upgrade pip \
    && pip install pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app dentro del contenedor
WORKDIR /app

# Copiar Pipfile y Pipfile.lock primero para aprovechar cache
COPY Pipfile Pipfile.lock /app/

# Instalar dependencias del proyecto
RUN pipenv install --system --deploy

# Copiar el resto del proyecto
COPY . /app

# Exponer puerto
EXPOSE 8000

# Comando por defecto: migraciones + Gunicorn
CMD bash -c "\
    echo '>>> Running migrations'; \
    python manage.py makemigrations --noinput || echo '>>> No new migrations'; \
    python.manage.py migrate --noinput; \
    echo '>>> Starting Gunicorn'; \
    exec gunicorn project.wsgi:application --bind 0.0.0.0:8000 \
"
