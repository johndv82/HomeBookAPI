#!/bin/sh
set -e


# Migraciones
echo ">>> Running makemigrations"
python manage.py makemigrations --noinput || echo ">>> No new migrations"

echo ">>> Running migrate"
python manage.py migrate --noinput

# Crear superuser si no existe
echo ">>> Creating superuser if missing"
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin') 
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print(">>> Superuser created:", email)
EOF

# Iniciar Gunicorn
echo ">>> Starting Gunicorn"
gunicorn project.wsgi:application --bind 0.0.0.0:8000
