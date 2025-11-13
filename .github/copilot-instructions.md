# Instruções do GitHub Copilot para Site Padrão CODATA

## Visão Geral do Projeto

Este é um **projeto Django/Wagtail CMS** para criação de portais governamentais padronizados. O projeto combina:

- **Backend**: Django 5.1.x + Wagtail 7.x (Python)
- **Frontend**: JavaScript/Webpack na pasta `frontend/`
- **Banco de Dados**: PostgreSQL (produção), SQLite (testes)
- **Ambiente**: Python 3.12+ e Node.js v22.13.1+
- **Gerenciamento de Versões**: asdf (recomendado), NVM, virtualenv, conda, pyenv

> **⚠️ IMPORTANTE - Configuração Local de Ambiente:**
> 
> Antes de executar qualquer comando Python ou npm, **SEMPRE pergunte ao usuário**:
> 1. "Qual comando você usa para ativar o ambiente virtual Python?" 
>    - Exemplos: `asdf install` (lê `.tool-versions`), `workon <nome>`, `source venv/bin/activate`, `conda activate <nome>`, `pyenv activate <nome>`
> 2. "Qual comando você usa para ativar a versão do Node.js (se aplicável)?"
>    - Exemplos: `asdf install` (gerencia Python + Node.js), `nvm use` (lê `.nvmrc`), `nvm use v22.13.1`, ou nenhum se usar versão global
> 
> **Arquivos de Configuração de Versão:**
> - `.tool-versions` - Configuração do asdf (Python 3.12.0 + Node.js 22.13.1)
> - `.nvmrc` - Configuração do NVM (Node.js 22)
> 
> Após obter as respostas, crie/atualize o arquivo `.github/copilot-local.md` com os comandos específicos.
> Este arquivo está no `.gitignore` e contém configurações específicas da máquina do desenvolvedor.

## Estrutura do Projeto

```
site-padrao/
├── frontend/              # Código JavaScript/CSS (Webpack, Babel, Jest)
├── agenda/                # App de agendas e eventos recorrentes
├── noticias/              # App de notícias e conteúdo
├── blocks/                # Blocos Wagtail StreamField reutilizáveis
├── core/                  # Configurações centrais e utilitários
│   ├── utils.py          # Utilitários de produção
│   └── utils_test.py     # Utilitários para testes
├── home/                  # Página inicial
├── institucional/         # Páginas institucionais
└── sitepadrao/            # Configurações Django
```

## Princípios de Desenvolvimento

### 1. **Código DRY (Don't Repeat Yourself)**
- ✅ SEMPRE verificar se já existe função/classe similar antes de criar nova
- ✅ Centralizar código reutilizável em arquivos de utilitários
- ✅ Utilitários de teste vão em `core/utils_test.py`
- ✅ Utilitários de produção vão em `core/utils.py` ou app específico
- ❌ NUNCA duplicar funções entre arquivos de teste

### 2. **Testes**
- ✅ SEMPRE criar testes para novas funcionalidades
- ✅ Usar `ensure_root_page()` de `core.utils_test` para setup de testes
- ✅ Rodar testes com: `python manage.py test <app> --keepdb`
- ✅ Executar coverage: `coverage run --source='.' manage.py test --keepdb`
- ✅ Normalizar locales nos testes: usar `get_supported_content_language_variant('pt-br')` retorna `'pt'`
- ✅ Inicializar `root.numchild = 0` em testes do Wagtail
- ✅ Sempre usar `root.refresh_from_db()` após operações de página

### 3. **Wagtail - Boas Práticas**
- ✅ Herdar de `PageSitePadrao` para páginas customizadas (já tem SEO, imagem destaque, descrição)
- ✅ Usar `StreamField` para conteúdo flexível, `TextField` para texto simples
- ✅ Migrations: usar `RenameField` para preservar dados (não `RemoveField` + `AddField`)
- ✅ Verificar conflitos de nomes de campos entre classe pai e filha
- ⚠️ Locale 'pt-br' é normalizado para 'pt' pelo Wagtail
- ⚠️ Treebeard requer `numchild` inicializado em páginas raiz

### 4. **Migrations**
- ✅ SEMPRE criar migrations para alterações de modelo
- ✅ Aplicar migrations após criação: `python manage.py migrate`
- ✅ Usar `RenameField` ao renomear campos (preserva dados)
- ✅ Verificar se migration foi aplicada antes de rodar testes
- ❌ NUNCA remover migrations já aplicadas

### 5. **Templates Django**
- ✅ Usar templatetags customizadas para lógica reutilizável
- ✅ Condicionar exibição de componentes com flags booleanas
- ✅ Exemplo: `{% if page.slideshow_imagens and page.images|length > 1 %}`
- ✅ Usar `{% load %}` para carregar templatetags necessárias
- ❌ NUNCA usar classes Bootstrap para cores (ex: `badge-primary`, `alert-info`)
- ✅ Criar classes personalizadas seguindo nomenclatura BEM

### 6. **CSS/SCSS - Organização e Padrões**

#### 6.1 Organização por App
- ✅ SEMPRE criar arquivos SCSS dentro da pasta do app correspondente
- ✅ Estrutura: `frontend/scss/{nome_do_app}/`
- ✅ Apenas componentes globais vão em `frontend/scss/core/`
- ❌ NÃO usar pasta `components/` genérica

```
frontend/scss/
├── agenda/              # App agenda
│   ├── index.scss      # Importa todos os arquivos do app
│   ├── _agenda.scss
│   ├── _agenda_escuro.scss
│   ├── _componente.scss
│   ├── _componente_cores.scss
│   └── _componente_cores_escuro.scss
├── noticias/           # App noticias
├── core/               # Apenas componentes globais
└── variables.scss      # Variáveis globais de cor
```

#### 6.2 Separação de Layout e Cores
- ✅ Criar 3 arquivos para cada componente:
  1. `_componente.scss` - Layout, estrutura, espaçamentos (SEM cores)
  2. `_componente_cores.scss` - Cores para tema claro
  3. `_componente_cores_escuro.scss` - Cores para tema escuro (envolvido em `[data-theme=dark]`)

**Importante**: No arquivo `_cores_escuro.scss`, SEMPRE envolver as regras com `[data-theme=dark] { }`

```scss
// ❌ ERRADO - _componente_cores_escuro.scss
.meu-componente {
  background-color: $color-dark-theme-bg;
}

// ✅ CORRETO - _componente_cores_escuro.scss
[data-theme=dark] {
  .meu-componente {
    background-color: $color-dark-theme-bg;
  }
}
```

#### 6.3 Uso de Variáveis de Cores
- ❌ NUNCA usar cores diretas: `#333`, `blue`, `rgba(...)`
- ✅ SEMPRE usar variáveis de `variables.scss`:
  - `$color-primary`, `$color-primary-darker`
  - `$color-on-primary` (texto sobre primary)
  - `$color-dark-theme-text`, `$color-dark-theme-border`
  - `$color-grey-600`, `$color-white`, `$color-black`

```scss
// ❌ ERRADO
.meu-componente {
  background-color: #396BBB;
  color: #fff;
}

// ✅ CORRETO
.meu-componente {
  background-color: $color-primary;
  color: $color-on-primary;
}
```

#### 6.4 Criação de Novas Cores
- Se cor não existe em `variables.scss`:
  1. Adicionar variável em `variables.scss` com nome semântico
  2. Criar versão escura se necessário
  3. Usar a variável nos arquivos de cores

#### 6.5 Nomenclatura BEM
- ✅ Usar padrão BEM (Block Element Modifier):
  - Bloco: `.agenda-recorrente`
  - Elemento: `.agenda-recorrente__info`, `.agenda-recorrente__title`
  - Modificador: `.agenda-recorrente__badge--highlight`

#### 6.6 Imports no index.scss
```scss
// frontend/scss/agenda/index.scss
@use './agenda.scss';
@use './agenda_escuro.scss';
@use './componente';
@use './componente_cores';
@use './componente_cores_escuro';
```

#### 6.7 Checklist CSS/SCSS
- [ ] Arquivos criados na pasta do app correto?
- [ ] 3 arquivos separados (layout, cores, cores_escuro)?
- [ ] Usado apenas variáveis de `variables.scss`?
- [ ] Nomenclatura BEM?
- [ ] Imports adicionados no `index.scss` do app?
- [ ] Evitadas classes Bootstrap de cores?
- [ ] Testado em tema claro E escuro?

### 7. **Git/Commits**
- ✅ Mensagens de commit seguem padrão: `tipo: descrição`
  - `feat:` nova funcionalidade
  - `fix:` correção de bug
  - `refactor:` refatoração de código
  - `test:` adição/modificação de testes
  - `docs:` documentação
- ✅ Corpo do commit lista alterações detalhadas com marcadores
- ✅ Mencionar número de testes passando no commit quando relevante

## Fluxo de Trabalho

### Antes de Implementar
1. Verificar se código similar já existe no projeto
2. Buscar por funções/classes relacionadas: `grep_search` ou `semantic_search`
3. Verificar imports existentes para evitar duplicação
4. Planejar usando `manage_todo_list` para tarefas complexas

### Durante Implementação
1. Seguir padrões DRY - reutilizar código existente
2. Criar testes junto com a implementação
3. Atualizar templates e migrations conforme necessário
4. Rodar `python manage.py check` para validar
5. Executar testes para garantir que nada quebrou

### Após Implementação
1. Rodar testes completos do app modificado
2. Verificar erros com `get_errors`
3. Criar commit descritivo
4. **DOCUMENTAÇÃO**: Perguntar ao usuário se deseja gerar documentação antes de criá-la

## Padrões de Código

### Python/Django
```python
# ✅ BOM - Herdar de PageSitePadrao
class MinhaPage(PageSitePadrao):
    # Já tem: descricao, imagem_destaque, get_imagem_destaque()
    conteudo = StreamField([...])

# ✅ BOM - Usar utils_test para testes
from core.utils_test import ensure_root_page

class MeuTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        cls.root_page.refresh_from_db()

# ❌ RUIM - Duplicar função
def ensure_root_page():  # Já existe em core.utils_test!
    ...
```

### JavaScript (frontend/)
- Usar ES6+ (Babel transpila)
- Testes com Jest
- Build com Webpack
- Comando build: `npm run build`
- Comando teste: `npm test`

### Templates
```django
{# ✅ BOM - Condicional clara #}
{% if page.slideshow_imagens and page.images|length > 1 %}
    <div class="swiper">...</div>
{% elif page.get_imagem_destaque %}
    <img src="{{ page.get_imagem_destaque }}" />
{% endif %}

{# ✅ BOM - Usar templatetag customizada #}
{% load sharing_tags %}
{% compartilhamento_social %}
```

## Problemas Comuns e Soluções

### Locale/Tradução
**Problema**: `Locale.DoesNotExist` para 'pt-br'
**Solução**: Wagtail normaliza para 'pt'. Usar `get_supported_content_language_variant()`

### Treebeard/Páginas
**Problema**: `AttributeError: 'NoneType' object has no attribute '_inc_path'`
**Solução**: Inicializar `root.numchild = 0` e fazer `root.refresh_from_db()` no setUp

### Conflito de Campos
**Problema**: Campo filho conflita com campo herdado da classe pai
**Solução**: Renomear campo filho (ex: `descricao` → `descricao_linha_do_tempo`)

### Migrations
**Problema**: Perda de dados ao alterar campo
**Solução**: Usar `RenameField` em vez de remover + adicionar

### Testes Quebrando
**Problema**: Testes funcionavam antes mas agora falham
**Solução**: 
1. Verificar se migrations foram aplicadas
2. Verificar `root.refresh_from_db()` no setUp
3. Limpar cache: `python manage.py test --keepdb=false`

## Comandos Úteis

> **Nota**: Os comandos de ativação de ambiente estão em `.github/copilot-local.md` (específico por desenvolvedor).
> Se o arquivo não existir, pergunte ao usuário os comandos de ativação de ambiente antes de executar.

```bash
# Ativar ambiente (veja .github/copilot-local.md)
# Exemplo com asdf: asdf install (lê .tool-versions automaticamente)
# Exemplo com virtualenv + nvm: workon codataSite && nvm use

# Testes
python manage.py test <app> --keepdb
coverage run --source='.' manage.py test --keepdb
coverage report

# Migrations
python manage.py makemigrations <app>
python manage.py migrate

# Validação
python manage.py check

# Frontend
npm install
npm run build
npm test

# GitLab CI (como é executado)
npm install && npm run build && npm test
python manage.py migrate
coverage run --source='.' manage.py test --keepdb
```

## Configurações de Settings

- Testes: `DJANGO_SETTINGS_MODULE=sitepadrao.settings.testing`
- Desenvolvimento: settings padrão
- Banco testes: SQLite in-memory
- Banco produção: PostgreSQL

## Apps Principais

### agenda/
- **Modelos**: `AgendaPage`, `AgendaDoDiaPage`
- **Funcionalidades**: Agendas com recorrência (diária, semanal, mensal, anual)
- **Testes**: test_models.py, test_views.py, test_wagtail_hooks.py

### noticias/
- **Modelos**: `NoticiasPage`, `NoticiasIndexPage`
- **Funcionalidades**: Notícias, categorias, tags, slideshow de imagens
- **Templates**: Suporta remote content e conteúdo local

### blocks/
- **Blocos reutilizáveis**: StreamField blocks para todo o site
- **Exemplos**: ListRedeSocial, CustomFormBlock, CarrosselBannerBlock

### core/
- **Modelos**: `PageSitePadrao`, `SiteSettings`, `ApiSettings`
- **Utilitários**: utils.py (produção), utils_test.py (testes)
- **Configurações**: Compartilhamento social, período eleitoral, cookies, analytics

## Checklist para Novas Features

- [ ] Verificar código duplicado existente (DRY)
- [ ] Criar/atualizar modelos
- [ ] Criar migrations
- [ ] Aplicar migrations
- [ ] Criar testes (mínimo 70% coverage)
- [ ] Atualizar templates se necessário
- [ ] Criar CSS/SCSS seguindo diretrizes (se aplicável):
  - [ ] Arquivos na pasta do app correto
  - [ ] 3 arquivos separados (layout, cores, cores_escuro)
  - [ ] Usar variáveis de `variables.scss`
  - [ ] Nomenclatura BEM
  - [ ] Testar tema claro e escuro
- [ ] Rodar `python manage.py check`
- [ ] Rodar testes do app: `python manage.py test <app> --keepdb`
- [ ] Verificar se não quebrou outros apps
- [ ] Criar commit descritivo
- [ ] **Perguntar antes de gerar documentação**

## Observações Importantes

1. **SEMPRE** verificar duplicação de código antes de criar nova função
2. **NUNCA** criar documentação markdown sem perguntar ao usuário
3. **SEMPRE** criar testes para novas funcionalidades
4. **SEMPRE** usar `ensure_root_page()` de `core.utils_test` em testes
5. **SEMPRE** normalizar locale 'pt-br' → 'pt' em testes Wagtail
6. **SEMPRE** inicializar `numchild = 0` em páginas raiz de testes
7. **SEMPRE** fazer `root.refresh_from_db()` após operações de página
8. Usar `RenameField` para preservar dados em migrations
9. Verificar conflitos de nomes entre classes pai/filho
10. Perguntar sobre documentação antes de gerar
11. **SEMPRE** perguntar sobre comandos de ambiente antes de executar pela primeira vez

## Contato e Suporte

- Projeto: Site Padrão CODATA-PB
- Stack: Django 5.1 + Wagtail 7.x + PostgreSQL
- Python: 3.12+
- Configurações de ambiente: veja `.github/copilot-local.md`
