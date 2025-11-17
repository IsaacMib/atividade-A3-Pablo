# Imagem base Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
COPY requirements/ requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia o projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs staticfiles media

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta
EXPOSE 8000

# Script de entrada
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "gestaoestoque.wsgi:application", "--bind", "0.0.0.0:8000"]
