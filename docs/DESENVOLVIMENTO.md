# NEUROATHENA - Guia de Desenvolvimento

## 🛠️ Ambiente de Desenvolvimento

### Estrutura de Settings

O projeto usa diferentes configurações por ambiente:

```python
# neuroathena/settings/
├── base.py        # Configurações compartilhadas
├── dev.py         # Desenvolvimento (DEBUG=True, SQLite)
├── testing.py     # Testes (SQLite in-memory)
└── production.py  # Produção (PostgreSQL, cache, etc)
```

Para alternar entre ambientes:
```bash
# Desenvolvimento (padrão)
python manage.py runserver

# Ou especifique:
export DJANGO_SETTINGS_MODULE=neuroathena.settings.production
python manage.py runserver
```

### Padrões de Código

#### Models
- Herdar de `PageNeuroAthena` para páginas Wagtail
- Use `StreamField` para conteúdo flexível
- Sempre criar migrations após alterações

```python
from core.models import PageNeuroAthena

class MinhaPage(PageNeuroAthena):
    conteudo = StreamField([...])
    
    content_panels = PageNeuroAthena.content_panels + [
        FieldPanel('conteudo'),
    ]
```

#### CSS/SCSS
- Organizar por app: `frontend/scss/{app_name}/`
- Separar layout e cores em arquivos diferentes
- Usar variáveis do `variables.scss`
- Nomenclatura BEM

```scss
// frontend/scss/noticias/_noticia.scss
.noticia {
  &__titulo { }
  &__conteudo { }
  &--destaque { }
}
```

#### Testes
- Cobertura mínima: 70%
- Um arquivo por tipo: `test_models.py`, `test_views.py`
- Usar `ensure_root_page()` do `core.utils_test`

```python
from core.utils_test import ensure_root_page

class MeuTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        cls.root_page.refresh_from_db()
```

## 🔄 Workflow Git

```bash
# Criar branch para feature
git checkout -b feature/minha-feature

# Fazer alterações
git add .
git commit -m "feat: adiciona nova funcionalidade"

# Push
git push origin feature/minha-feature

# Criar Pull Request no GitHub/GitLab
```

### Padrão de Commits
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `refactor:` Refatoração de código
- `test:` Adicionar/modificar testes
- `docs:` Documentação
- `style:` Formatação, CSS

## 📦 Dependências

### Adicionar Nova Dependência

1. Adicione em `requirements.txt`
2. Instale: `pip install -r requirements.txt`
3. Commit o arquivo atualizado

### Frontend (JavaScript/SCSS)

```bash
# Instalar dependências Node
npm install

# Build
npm run build

# Watch (desenvolvimento)
npm run watch

# Testes
npm test
```

## 🧪 Testes

### Rodar Testes

```bash
# Todos os testes
python manage.py test

# App específico
python manage.py test noticias

# Com coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera htmlcov/index.html
```

### Criar Testes

```python
from django.test import TestCase
from .models import MinhaModel

class MinhaModelTestCase(TestCase):
    def setUp(self):
        self.obj = MinhaModel.objects.create(nome="Teste")
    
    def test_criacao(self):
        self.assertEqual(self.obj.nome, "Teste")
```

## 🐳 Docker (Opcional)

```bash
# Build
docker-compose build

# Run
docker-compose up

# Stop
docker-compose down
```

## 🔐 Variáveis de Ambiente

Crie `.env` na raiz (não commitar!):

```env
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados
DATABASE_URL=postgresql://user:pass@localhost/neuroathena

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Cache
REDIS_URL=redis://localhost:6379/0
```

## 📚 Recursos

- Django Docs: https://docs.djangoproject.com/
- Wagtail Docs: https://docs.wagtail.org/
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
