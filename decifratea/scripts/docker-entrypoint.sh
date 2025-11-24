#!/bin/sh
set -e

echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Banco de dados disponível"

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando aplicação..."
exec "$@"
