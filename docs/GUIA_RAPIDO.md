# NEUROATHENA - Guia de Início Rápido

## 🚀 Setup Rápido (5 minutos)

### 1. Pré-requisitos
- Python 3.12+
- Node.js 22+ (opcional, para frontend)
- Git

### 2. Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd atividade-A3-Pablo

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Windows: Instale python-magic-bin
pip install python-magic-bin

# Configure banco de dados
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver
```

### 3. Acesse o Sistema
- **Frontend**: http://127.0.0.1:8000
- **Admin Django**: http://127.0.0.1:8000/django-admin/
- **Admin Wagtail**: http://127.0.0.1:8000/admin/

## 📁 Estrutura do Projeto

```
neuroathena/           # Configurações Django
├── settings/
│   ├── base.py       # Configurações base
│   ├── dev.py        # Desenvolvimento
│   └── production.py # Produção
├── urls.py           # URLs principais
└── wsgi.py           # WSGI config

core/                  # App central (utils, modelos base)
home/                  # Página inicial
noticias/             # Sistema de notícias
lgpd/                 # Conformidade LGPD
triagem_ia/           # Sistema de triagem IA
painel_diario/        # Painel de desenvolvimento
blocks/               # Blocos Wagtail reutilizáveis
search/               # Sistema de busca

frontend/             # Assets frontend
├── js/              # JavaScript
└── scss/            # Estilos SASS
```

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
python manage.py runserver
python manage.py migrate
python manage.py makemigrations

# Testes
python manage.py test
pytest
coverage run -m pytest
coverage report

# Frontend (se necessário)
npm install
npm run build
npm run watch

# Banco de dados
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

## 🐛 Troubleshooting

### Erro: "libmagic não encontrado" (Windows)
```bash
pip install python-magic-bin
```

### Erro: "ExecutionPolicy" (Windows PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Erro: PostgreSQL connection
Configure `.env` com suas credenciais:
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 🤖 Athena - Sistema de IA

**Athena** é o sistema de IA multimodal (pasta `athena-ai/`):

- **Análise de Vídeo**: MediaPipe, InsightFace
- **Análise de Áudio**: Silero VAD, Wav2Vec2
- **Análise de Texto**: BERT/BERTimbau
- **Fusão Multimodal**: CLIP, ImageBind

Ver: `athena-ai/README.md`

## 📖 Mais Informações

- **Desenvolvimento**: Ver `docs/DESENVOLVIMENTO.md`
- **Arquitetura**: Ver `docs/ARQUITETURA.md`
