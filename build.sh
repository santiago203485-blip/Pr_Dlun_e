#!/usr/bin/env bash
# Script de construcción para Render (y cualquier host Linux)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py crear_admin
# Carga los datos de prueba solo si se pide (CARGAR_DATOS_DEMO=True)
if [ "${CARGAR_DATOS_DEMO:-False}" = "True" ]; then
  python manage.py datos_demo
fi
