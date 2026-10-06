# Backend Django servido con gunicorn (modo tipo producción para Docker).
# El modo desarrollo (python manage.py runserver) no usa este archivo.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias primero, para aprovechar la caché de capas al cambiar código.
# gunicorn se instala aquí y no en requirements.txt: solo funciona en Linux y
# el modo desarrollo en Windows no lo necesita.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

# Usuario sin privilegios; necesita escribir en /app para crear db.sqlite3.
RUN useradd --create-home --uid 1000 app
COPY --chown=app:app . .
RUN chown app:app /app
USER app

EXPOSE 8000

# Las migraciones solo crean las tablas internas de Django en SQLite (no hay
# datos del usuario que persistir). Timeout alto: sympy puede tardar en
# algunos despejes o derivadas.
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile -"]
