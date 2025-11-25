# NEUROATHENA - Arquitetura do Sistema

## 📐 Visão Geral

Sistema Django/Wagtail CMS para triagem precoce de autismo com IA multimodal.

### Stack Tecnológica

- **Backend**: Django 5.1 + Wagtail 7.x (Python 3.12+)
- **Frontend**: JavaScript (ES6+), SCSS, Webpack
- **Banco**: PostgreSQL (prod), SQLite (dev/test)
- **Cache**: Redis
- **IA**: Athena - Modelos multimodais (texto, imagem, vídeo, áudio)

## 🏗️ Estrutura de Apps

### Core Apps

#### `core/`
Configurações centrais e modelos base.

- **Models**: `PageNeuroAthena`, `PageNeuroAthenaIndex`
- **Utils**: Funções compartilhadas
- **Settings**: Configurações de site via Wagtail

#### `home/`
Página inicial com blocos StreamField dinâmicos.

#### `noticias/`
Sistema de notícias/blog com:
- Categorias e tags
- Slideshow de imagens
- Sistema de busca integrado

#### `blocks/`
Blocos Wagtail reutilizáveis:
- Carrossel de banners
- Listas de redes sociais
- Formulários customizados

### Apps de Funcionalidade

#### `triagem_ia/`
Sistema de triagem multimodal para autismo.
- Análise de texto, imagem, vídeo, áudio
- Modelos de IA integrados
- Dashboard de resultados

#### `painel_diario/`
Registro diário de desenvolvimento infantil.
- Formulários de acompanhamento
- Gráficos de evolução
- Alertas automatizados

#### `lgpd/`
Conformidade com proteção de dados.
- Termos de uso
- Política de privacidade
- Gestão de consentimento

### Apps Auxiliares

#### `search/`
Busca global no site via Wagtail.

## 🔄 Fluxo de Dados

```
Usuario → Wagtail Page → StreamField Blocks → Template → Frontend
                                             ↓
                                        Database (PostgreSQL)
                                             ↓
                                        Cache (Redis)
```

## 🎨 Frontend

### Estrutura SCSS

```
frontend/scss/
├── variables.scss         # Variáveis globais
├── main.scss             # Entry point
├── core/                 # Componentes globais
├── neuroathena/          # Tema do site
│   ├── header.scss
│   ├── footer.scss
│   └── menu.scss
├── noticias/             # App noticias
└── {app_name}/           # Outros apps
```

### Tema Escuro

Suporte automático via `[data-theme="dark"]`:
```scss
.componente {
  background: $color-light-bg;
}

[data-theme="dark"] .componente {
  background: $color-dark-bg;
}
```

## 🔐 Segurança

### Proteções Implementadas

- **CSRF**: Tokens em todos os formulários
- **CSP**: Content Security Policy configurado
- **HTTPS**: Forçado em produção
- **LGPD**: Gestão de dados pessoais
- **Auth**: Django Allauth + SSO (opcional)

### Variáveis Sensíveis

Nunca commitar:
- `SECRET_KEY`
- Credenciais de banco
- API keys
- Tokens de serviços

Use `.env` e `python-decouple`.

## 📊 Banco de Dados

### Modelos Principais

```python
# Hierarquia de páginas Wagtail
Page (Wagtail)
└── PageNeuroAthena (core)
    ├── HomePage (home)
    ├── NoticiasPage (noticias)
    ├── LGPDPage (lgpd)
    └── ...

# Índices
PageNeuroAthenaIndex (core)
└── NoticiasIndexPages (noticias)
```

### Migrations

```bash
# Criar
python manage.py makemigrations

# Aplicar
python manage.py migrate

# Reverter
python manage.py migrate app_name 0001

# Ver SQL
python manage.py sqlmigrate app_name 0001
```

## 🚀 Deploy

### Checklist de Produção

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` único e seguro
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Database: PostgreSQL
- [ ] Static files: Whitenoise ou S3
- [ ] Media files: S3 ou similar
- [ ] Cache: Redis configurado
- [ ] HTTPS ativo
- [ ] Backup automático
- [ ] Monitoring configurado

### Variáveis de Ambiente (Produção)

```env
DJANGO_SETTINGS_MODULE=neuroathena.settings.production
SECRET_KEY=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ALLOWED_HOSTS=exemplo.com,www.exemplo.com
```

## 🔍 Monitoring

### Logs

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Mensagem informativa")
logger.error("Erro", exc_info=True)
```

### Performance

- Use `select_related()` e `prefetch_related()`
- Cache queries pesadas com Redis
- Otimize imagens (Wagtail faz automaticamente)
- Use CDN para static files

## 📱 APIs (Futuro)

### Django REST Framework

```python
from rest_framework import viewsets
from .models import MinhaModel
from .serializers import MinhaModelSerializer

class MinhaModelViewSet(viewsets.ModelViewSet):
    queryset = MinhaModel.objects.all()
    serializer_class = MinhaModelSerializer
```

## 🧩 Extensibilidade

### Adicionar Novo App

1. Criar app: `python manage.py startapp novo_app`
2. Adicionar em `INSTALLED_APPS` (settings/base.py)
3. Criar models, views, templates
4. Migrations: `python manage.py makemigrations`
5. Registrar no Wagtail admin (se necessário)

### Criar Novo Bloco StreamField

```python
from wagtail import blocks

class MeuBloco(blocks.StructBlock):
    titulo = blocks.CharBlock()
    conteudo = blocks.RichTextBlock()
    
    class Meta:
        template = 'blocks/meu_bloco.html'
        icon = 'doc-full'
```
