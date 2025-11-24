# 🚀 Início Rápido - NeuroPrev Multimodal

Guia para iniciar o desenvolvimento do projeto.

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter:

- [x] Python 3.12+ instalado
- [x] Node.js 22+ instalado (para frontend)
- [ ] PostgreSQL 14+ instalado
- [ ] Redis instalado
- [x] Git configurado
- [x] Ambiente virtual Python ativo

---

## 📦 1. Instalação de Dependências Adicionais

### PostgreSQL (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Redis (Ubuntu/Debian)
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Verificar Instalações
```bash
psql --version         # PostgreSQL 14.x
redis-cli --version    # redis-cli 6.x ou superior
python --version       # Python 3.12.x
node --version         # v22.x
```

---

## 🗄️ 2. Configurar Banco de Dados

### Criar Banco PostgreSQL

```bash
# Acessar PostgreSQL como superusuário
sudo -u postgres psql

# Dentro do psql, executar:
CREATE DATABASE neuroprev_dev;
CREATE USER neuroprev_user WITH PASSWORD 'senha_segura_aqui';
ALTER ROLE neuroprev_user SET client_encoding TO 'utf8';
ALTER ROLE neuroprev_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE neuroprev_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE neuroprev_dev TO neuroprev_user;
\q
```

### Atualizar Settings

Criar arquivo `.env` na raiz do projeto:

```bash
# .env
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui-gere-com-django-secret-key-generator
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=neuroprev_dev
DB_USER=neuroprev_user
DB_PASSWORD=senha_segura_aqui
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (desenvolvimento - console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

Atualizar `sitepadrao/settings/dev.py`:

```python
import os
from .base import *

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'neuroprev_dev'),
        'USER': os.getenv('DB_USER', 'neuroprev_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
```

Instalar dependências:

```bash
pip install python-dotenv psycopg2-binary django-redis celery
```

---

## 🔧 3. Criar Apps Django

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Criar apps principais
python manage.py startapp triagem_ia
python manage.py startapp painel_diario
python manage.py startapp comunidade
python manage.py startapp biblioteca_conteudos
```

### Adicionar aos INSTALLED_APPS

Editar `sitepadrao/settings/base.py`:

```python
INSTALLED_APPS = [
    # ... apps existentes ...
    
    # Apps do projeto
    'home',
    'core',
    'blocks',
    'noticias',
    'institucional',
    
    # Novos apps NeuroPrev
    'triagem_ia',
    'painel_diario',
    'comunidade',
    'biblioteca_conteudos',
    
    # ... resto dos apps ...
]
```

---

## 👤 4. Criar User Model Customizado

Criar arquivo `core/models.py` (ou atualizar existente):

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Modelo de usuário customizado para NeuroPrev
    """
    TIPO_USUARIO_CHOICES = [
        ('responsavel', 'Responsável/Pai/Mãe'),
        ('profissional', 'Profissional de Saúde'),
        ('admin', 'Administrador'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='responsavel'
    )
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    aceite_termos = models.BooleanField(default=False)
    data_aceite_termos = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_usuario_display()})"


class ConsentimentoLGPD(models.Model):
    """
    Registro de consentimento LGPD do usuário
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    aceite_coleta_dados = models.BooleanField(default=False)
    aceite_analise_ia = models.BooleanField(default=False)
    aceite_pesquisa_anonima = models.BooleanField(default=False)
    aceite_compartilhamento_profissionais = models.BooleanField(default=False)
    data_aceite = models.DateTimeField(auto_now_add=True)
    data_revogacao = models.DateTimeField(null=True, blank=True)
    ip_aceite = models.GenericIPAddressField()
    
    class Meta:
        verbose_name = 'Consentimento LGPD'
        verbose_name_plural = 'Consentimentos LGPD'
    
    def __str__(self):
        return f"Consentimento de {self.usuario.username}"


class LogAcesso(models.Model):
    """
    Log de acessos a dados sensíveis (auditoria LGPD)
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    acao = models.CharField(max_length=100)
    tabela_acessada = models.CharField(max_length=100, blank=True)
    objeto_id = models.IntegerField(null=True, blank=True)
    ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data_hora}"


class SolicitacaoExclusao(models.Model):
    """
    Solicitações de exclusão de dados (Right to be Forgotten)
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_processamento', 'Em Processamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    motivo = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    processado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='exclusoes_processadas'
    )
    
    class Meta:
        verbose_name = 'Solicitação de Exclusão'
        verbose_name_plural = 'Solicitações de Exclusão'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação #{self.id} - {self.usuario.username} - {self.get_status_display()}"
```

Atualizar `sitepadrao/settings/base.py`:

```python
# User Model Customizado
AUTH_USER_MODEL = 'core.Usuario'
```

---

## 🔄 5. Aplicar Migrations

```bash
# Criar migrations para o novo User model
python manage.py makemigrations core

# Aplicar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

---

## ⚙️ 6. Configurar Celery

Criar arquivo `sitepadrao/celery.py`:

```python
import os
from celery import Celery

# Define o settings padrão do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitepadrao.settings.dev')

app = Celery('neuroprev')

# Carregar configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobrir tasks em todos os apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

Atualizar `sitepadrao/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

Testar Celery:

```bash
# Terminal 1: Iniciar worker Celery
celery -A sitepadrao worker --loglevel=info

# Terminal 2: Testar task
python manage.py shell
>>> from sitepadrao.celery import debug_task
>>> debug_task.delay()
```

---

## 🧪 7. Configurar Testes

Instalar pytest:

```bash
pip install pytest pytest-django pytest-cov
```

Criar `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = sitepadrao.settings.testing
python_files = tests.py test_*.py *_tests.py
addopts = 
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=70
    --strict-markers
    -v
```

Criar `conftest.py` na raiz:

```python
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

@pytest.fixture
def usuario_teste(db):
    from core.models import Usuario
    return Usuario.objects.create_user(
        username='teste',
        email='teste@neuroprev.com',
        password='senha123',
        tipo_usuario='responsavel'
    )
```

Rodar testes:

```bash
pytest
```

---

## 🎨 8. Atualizar Frontend

Rebuild do frontend com logos corretas:

```bash
npm run build
```

Coletar arquivos estáticos:

```bash
python manage.py collectstatic --noinput
```

---

## 🚀 9. Iniciar Desenvolvimento

```bash
# Terminal 1: Servidor Django
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Celery Worker
celery -A sitepadrao worker --loglevel=info

# Terminal 3: Celery Beat (agendador) - quando necessário
celery -A sitepadrao beat --loglevel=info
```

Acessar:
- Frontend: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Wagtail: http://localhost:8000/cms/

---

## 📝 10. Próximos Passos

Após completar o setup inicial:

1. **Criar modelos de Triagem** (`triagem_ia/models.py`)
2. **Implementar questionários M-CHAT-R e Q-CHAT**
3. **Criar interface de triagem**
4. **Implementar análise MVP (regras + NLP básico)**
5. **Criar painel diário**

Consulte `docs/PLANEJAMENTO.md` para cronograma completo.

---

## 🆘 Troubleshooting

### Erro de conexão PostgreSQL
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Erro de conexão Redis
```bash
# Verificar se Redis está rodando
redis-cli ping  # Deve retornar "PONG"

# Reiniciar Redis
sudo systemctl restart redis
```

### Erro de migrations
```bash
# Resetar banco (APENAS EM DESENVOLVIMENTO!)
python manage.py migrate --run-syncdb
python manage.py migrate
```

### Celery não encontra tasks
```bash
# Verificar se __init__.py existe em cada app
# Verificar se celery.py está importado em sitepadrao/__init__.py
```

---

## 📚 Documentação Adicional

- [ARQUITETURA.md](ARQUITETURA.md) - Arquitetura completa do sistema
- [PLANEJAMENTO.md](PLANEJAMENTO.md) - Cronograma de desenvolvimento
- [README.md](../README.md) - Visão geral do projeto

---

*Última atualização: 24/11/2025*
