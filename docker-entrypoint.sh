#!/bin/sh
set -e

# Se DATABASE_URL não estiver definida, monta a URL a partir das outras variáveis
if [ -z "$DATABASE_URL" ]; then
  DATABASE_URL="postgresql://${DATABASE_USERNAME}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}"
fi

until psql $DATABASE_URL -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

>&2 echo "[Entrypoint] Comando recebido: $1"

if [ "$DJANGO_SETTINGS_DEBUG" = "true" ]; then
    echo "[Entrypoint] Ambiente: DESENVOLVIMENTO (DEBUG)"
    if [ "$1" != "runserver" ] && [ "$1" != "/venv/bin/uwsgi" ] && [ "$1" != "uwsgi" ]; then
        echo "[Entrypoint] Executando comando customizado: $@"
        exec "$@"
    fi
    # Ambiente de desenvolvimento: roda runserver com browser-reload
    if [ "$NPM_WATCH" = "on" ]; then
      echo "[Entrypoint] Iniciando npm run watch em background"
      npm install
      npm run build:dev
      npm run watch &
    fi
    echo "[Entrypoint] Iniciando Django runserver em modo debug"
    exec /venv/bin/python manage.py runserver 0.0.0.0:8080
else
    echo "[Entrypoint] Ambiente: PRODUÇÃO"
    if [ "$1" = '/venv/bin/uwsgi' ]; then
        echo "[Entrypoint] Executando migrate antes do uwsgi"
        /venv/bin/python manage.py migrate --noinput
    fi
    if [ "x$DJANGO_LOAD_INITIAL_DATA" = 'xon' ]; then
        echo "[Entrypoint] Carregando dados iniciais"
    	/venv/bin/python manage.py load_initial_data
    fi
    if [ "$NPM_WATCH" = "on" ]; then
      echo "[Entrypoint] Iniciando npm run watch em background"
      npm run watch &
    fi
    echo "[Entrypoint] Executando comando: $@"
    exec "$@"
fi

if [ "$DJANGO_RUN_MIGRATE" = "1" ]
then
  python manage.py migrate --no-input
fi