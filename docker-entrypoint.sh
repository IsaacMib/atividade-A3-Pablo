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

if [ "$1" = '/venv/bin/uwsgi' ]; then
    /venv/bin/python manage.py migrate --noinput
fi

if [ "x$DJANGO_LOAD_INITIAL_DATA" = 'xon' ]; then
	/venv/bin/python manage.py load_initial_data
fi

exec "$@"
