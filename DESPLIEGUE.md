# Despliegue gratuito de Dlune

El proyecto queda listo para producción con variables de entorno (ver `.env.example`):

| Variable | Para qué sirve |
|---|---|
| `SECRET_KEY` | Clave secreta de Django (larga y aleatoria) |
| `DEBUG` | `False` en producción |
| `ALLOWED_HOSTS` | Dominio del sitio, por ejemplo `tuusuario.pythonanywhere.com` |
| `DATABASE_URL` | Opcional. PostgreSQL; si no existe se usa SQLite |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL` | Opcional. `python manage.py crear_admin` crea el administrador |
| `DEMO_PASSWORD` | Opcional. Si existe, `datos_demo` crea los usuarios de prueba con esa clave |

Los archivos estáticos los sirve WhiteNoise y las imágenes subidas las sirve Django (`SERVE_MEDIA=True`).

## Opción recomendada: PythonAnywhere (gratis, sin tarjeta)

Ventaja: el disco es permanente, así que SQLite y las imágenes subidas no se pierden.

1. Sube el proyecto a GitHub (sin `venv`, `db.sqlite3` ni `media`; ya están en `.gitignore`).
2. Crea una cuenta en https://www.pythonanywhere.com (plan *Beginner*, gratis).
3. Abre una consola **Bash** y ejecuta:
   ```bash
   git clone https://github.com/TU_USUARIO/Pr_Dlune.git
   cd Pr_Dlune
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   export DEBUG=False SECRET_KEY='pon-aqui-tu-clave' ALLOWED_HOSTS=TU_USUARIO.pythonanywhere.com
   python manage.py migrate
   python manage.py collectstatic --no-input
   python manage.py datos_demo
   python manage.py createsuperuser
   ```
4. En la pestaña **Web** → *Add a new web app* → *Manual configuration* → **Python 3.13**.
5. En *Virtualenv* escribe: `/home/TU_USUARIO/Pr_Dlune/venv`
6. Abre el archivo **WSGI** y deja solo esto:
   ```python
   import os, sys
   sys.path.insert(0, '/home/TU_USUARIO/Pr_Dlune')
   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
   os.environ['DEBUG'] = 'False'
   os.environ['SECRET_KEY'] = 'pon-aqui-tu-clave'
   os.environ['ALLOWED_HOSTS'] = 'TU_USUARIO.pythonanywhere.com'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
7. En *Static files* agrega: URL `/media/` → carpeta `/home/TU_USUARIO/Pr_Dlune/media`.
8. Activa *Force HTTPS* y pulsa **Reload**. El sitio queda en `https://TU_USUARIO.pythonanywhere.com`.

Para actualizar después: `git pull`, `python manage.py migrate`, `python manage.py collectstatic --no-input` y **Reload**.

## Opción 2: Render (gratis, con PostgreSQL)

El repositorio trae `render.yaml` y `build.sh`.

1. Sube el proyecto a GitHub (asegúrate de que `build.sh` sea ejecutable: `git add --chmod=+x build.sh`).
2. En https://render.com → **New** → **Blueprint** → elige el repositorio.
3. Completa `ADMIN_USERNAME` y `ADMIN_PASSWORD` cuando lo pida y crea los servicios.

Ten en cuenta: el plan gratuito se "duerme" tras 15 minutos sin visitas (la primera carga tarda), el disco
no es permanente (las imágenes subidas se borran en cada despliegue) y la base PostgreSQL gratuita vence a los 30 días.

## Verificación local en modo producción

```bash
set DEBUG=False
set SECRET_KEY=una-clave-de-prueba-larga
set SECURE_SSL_REDIRECT=False
venv\Scripts\python.exe manage.py collectstatic --no-input
venv\Scripts\python.exe manage.py check --deploy
```

`check --deploy` avisa que el correo usa el backend de consola: el sistema no envía correos, así que no afecta.
