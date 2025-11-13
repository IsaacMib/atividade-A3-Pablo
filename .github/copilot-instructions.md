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
- ⚠️ **IMPORTANTE**: Ao modificar funcionalidades existentes, ATUALIZAR os testes para refletir o novo comportamento
- ❌ NUNCA alterar o código de produção para fazer os testes passarem - ajuste os testes para validar o comportamento correto
- ✅ Testes devem validar o comportamento atual do código, não o comportamento antigo
- ✅ Quando hooks/signals alteram dados automaticamente, os testes devem verificar os dados APÓS o processamento
- ✅ Usar métodos de teste apropriados:
  - `assertEqual()` para valores exatos
  - `assertIn()` para verificar se substring existe
  - `assertTrue()/assertFalse()` para condições booleanas
  - `assertRaises()` para verificar exceções
- ✅ Nomenclatura de testes: `test_<funcionalidade>_<cenario>` (ex: `test_titulo_agenda_recorrente_com_data`)
- ✅ Cobertura mínima: 70% de code coverage
- ✅ Testes de integração para fluxos completos (create → publish → verify)
- ✅ Testes unitários para funções helper isoladas

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

**Documentação completa**: `docs/diretrizes-css-scss.md`

### 7. **Acessibilidade (A11y)**

**Padrões a seguir:**
- WCAG 2.1 Level AA: https://www.w3.org/WAI/WCAG21/quickref/
- Axe DevTools Rules: https://dequeuniversity.com/rules/axe/4.10

**Ferramentas de validação:**
- Axe DevTools (extensão do navegador)
- WAVE (Web Accessibility Evaluation Tool)
- Lighthouse (Chrome DevTools)

#### 7.1 HTML Semântico
- ✅ Usar elementos HTML semânticos apropriados (WCAG 1.3.1 - Info and Relationships)
- ❌ NUNCA usar `<strong>` ou `<b>` em parágrafos como se fossem headings
- ✅ Usar hierarquia correta de headings (h1 → h2 → h3...) sem pular níveis
- ✅ Usar `<dl>`, `<dt>`, `<dd>` para listas de definição/dados chave-valor
- ✅ Usar `<button>` para ações, `<a>` para navegação
- ✅ Elementos de formulário devem ter labels associados (`<label for="id">`)

```html
<!-- ❌ ERRADO - strong como heading -->
<div>
  <strong>Autoridade:</strong> Nome da autoridade
</div>

<!-- ✅ CORRETO - elementos semânticos -->
<dl>
  <dt>Autoridade:</dt>
  <dd>Nome da autoridade</dd>
</dl>
```

#### 7.2 Contraste de Cores (WCAG 1.4.3)
- ✅ Garantir contraste mínimo WCAG AA:
  - Texto normal: 4.5:1
  - Texto grande (18pt+ ou 14pt+ negrito): 3:1
- ✅ Testar em ambos os temas (claro e escuro)
- ✅ Texto sobre fundos coloridos deve ter contraste adequado
- ✅ Usar ferramentas como WebAIM Contrast Checker

#### 7.3 Estrutura e Navegação
- ✅ Landmarks ARIA quando apropriado (`main`, `nav`, `aside`, `header`, `footer`)
- ✅ Labels descritivos em formulários (WCAG 3.3.2)
- ✅ Alternativas textuais para imagens (`alt`) - WCAG 1.1.1
- ✅ Foco visível em elementos interativos (WCAG 2.4.7)
- ✅ Links descritivos - evitar "clique aqui" (WCAG 2.4.4)
- ✅ Skip links para navegação rápida

#### 7.4 Responsividade e Zoom (WCAG 1.4.4, 1.4.10)
- ✅ Testar em diferentes tamanhos de tela
- ✅ Garantir que texto possa ser ampliado até 200% sem perda de conteúdo
- ✅ Evitar scroll horizontal em dispositivos móveis
- ✅ Viewport não deve bloquear zoom: `<meta name="viewport" content="width=device-width, initial-scale=1">`

#### 7.5 Interatividade
- ✅ Navegação por teclado funcionando (Tab, Enter, Setas)
- ✅ Ordem de foco lógica (WCAG 2.4.3)
- ✅ Modais devem capturar foco (focus trap)
- ✅ Estados de erro claramente identificados (WCAG 3.3.1)

#### 7.6 Checklist de Acessibilidade
- [ ] HTML semântico usado corretamente? (WCAG 1.3.1)
- [ ] Hierarquia de headings lógica sem pulos? (WCAG 1.3.1)
- [ ] Contraste de cores adequado 4.5:1? (WCAG 1.4.3)
- [ ] Labels e textos alternativos presentes? (WCAG 1.1.1, 3.3.2)
- [ ] Elementos interativos têm foco visível? (WCAG 2.4.7)
- [ ] Navegação por teclado funciona? (WCAG 2.1.1)
- [ ] Testado com Axe DevTools sem erros?
- [ ] Testado com leitor de tela (NVDA/JAWS/VoiceOver)?

### 8. **Git/Commits**
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
- [ ] Validar acessibilidade (se aplicável):
  - [ ] HTML semântico correto (WCAG 1.3.1)
  - [ ] Hierarquia de headings sem pulos
  - [ ] Contraste de cores 4.5:1 (WCAG 1.4.3)
  - [ ] Labels e alt text presentes (WCAG 1.1.1, 3.3.2)
  - [ ] Navegação por teclado funciona
  - [ ] Testado com Axe DevTools sem erros
- [ ] Rodar `python manage.py check`
- [ ] Rodar testes do app: `python manage.py test <app> --keepdb`
- [ ] Verificar se não quebrou outros apps
- [ ] Criar commit descritivo
- [ ] **Perguntar antes de gerar documentação**

## Estrutura e Boas Práticas de Testes

### 8.1 Quando Criar Testes
- ✅ **SEMPRE** criar testes para:
  - Novas funcionalidades (models, views, hooks, templatetags)
  - Correções de bugs (teste deve falhar sem o fix, passar com o fix)
  - Modificações em hooks do Wagtail (after_create_page, after_publish_page, etc.)
  - Alterações em lógica de negócio (recorrência, agendamento, permissões)
  - Novos métodos em models (get_*, save, clean, etc.)
  - APIs e serializers
  - Utilitários e helpers

### 8.2 Estrutura de Arquivos de Teste
```
app/
├── tests.py              # Testes gerais (se único arquivo)
├── test_models.py        # Testes de models
├── test_views.py         # Testes de views
├── test_wagtail_hooks.py # Testes de hooks do Wagtail
├── test_templatetags.py  # Testes de templatetags
└── test_utils.py         # Testes de utilitários
```

### 8.3 Nomenclatura de Testes
- Padrão: `test_<funcionalidade>_<cenario>_<resultado_esperado>`
- Exemplos:
  - `test_titulo_agenda_recorrente_com_data`
  - `test_slug_agenda_normal_nao_modificado`
  - `test_hook_publish_apenas_agenda_recorrente`
  - `test_validacao_data_fim_maior_que_inicio`

### 8.4 Estrutura de Classe de Teste

```python
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from wagtail.models import Locale
from core.utils_test import ensure_root_page
from .models import MeuModel

class MeuModelTestCase(TestCase):
    """Testes para MeuModel."""
    
    @classmethod
    def setUpTestData(cls):
        """Setup executado uma vez para toda a classe."""
        # Setup de dados compartilhados
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0  # Wagtail treebeard
        cls.root_page.save()
        cls.root_page.refresh_from_db()
        
        cls.locale = Locale.get_default()
    
    def setUp(self):
        """Setup executado antes de cada teste."""
        # Setup específico por teste
        self.factory = RequestFactory()
        self.root_page.refresh_from_db()
    
    def test_funcionalidade_basica(self):
        """Testa comportamento básico."""
        # Arrange (preparar)
        obj = MeuModel.objects.create(titulo="Teste")
        
        # Act (executar)
        resultado = obj.get_titulo_formatado()
        
        # Assert (verificar)
        self.assertEqual(resultado, "TESTE")
```

### 8.5 Testes de Hooks do Wagtail

```python
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from wagtail.models import Page
from core.utils_test import ensure_root_page
from .wagtail_hooks import (
    do_after_minha_page_create,
    do_after_minha_page_publish,
    atualizar_minha_funcionalidade,
)
from .models import MinhaPage

class WagtailHooksTestCase(TestCase):
    """Testes para hooks do Wagtail."""
    
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()
        cls.root_page.numchild = 0
        cls.root_page.save()
        cls.root_page.refresh_from_db()
        
        cls.factory = RequestFactory()
    
    def setUp(self):
        self.root_page.refresh_from_db()
    
    def _create_request_with_messages(self):
        """Helper para criar request com sistema de mensagens."""
        request = self.factory.post('/')
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request
    
    def test_hook_create_modifica_titulo(self):
        """Hook after_create deve modificar título automaticamente."""
        # Arrange
        request = self._create_request_with_messages()
        page = MinhaPage(
            title="Título Original",
            slug="titulo-original",
        )
        self.root_page.add_child(instance=page)
        page.save()
        
        # Act
        do_after_minha_page_create(request, page)
        page.refresh_from_db()
        
        # Assert
        self.assertIn("Título Original", page.title)
        # Verificar modificação específica do hook
        self.assertTrue(page.title.endswith("- Modificado"))
    
    def test_hook_publish_apenas_quando_condicao_ativada(self):
        """Hook after_publish deve processar apenas quando condição ativa."""
        # Arrange
        request = self._create_request_with_messages()
        page = MinhaPage(
            title="Teste",
            condicao_ativada=False,  # Condição desativada
        )
        self.root_page.add_child(instance=page)
        titulo_original = page.title
        
        # Act
        do_after_minha_page_publish(request, page)
        page.refresh_from_db()
        
        # Assert - título NÃO deve mudar
        self.assertEqual(page.title, titulo_original)
```

### 8.6 Asserções Comuns

```python
# Igualdade exata
self.assertEqual(valor, esperado)
self.assertNotEqual(valor, nao_esperado)

# Substring/Contém
self.assertIn("substring", string_completa)
self.assertNotIn("ausente", string_completa)

# Booleanos
self.assertTrue(condicao)
self.assertFalse(condicao)
self.assertIsNone(valor)
self.assertIsNotNone(valor)

# Exceções
with self.assertRaises(ValueError):
    funcao_que_deve_falhar()

# Querysets/Listas
self.assertEqual(len(lista), 3)
self.assertQuerySetEqual(qs, esperado, transform=str)

# HTTP Responses
self.assertEqual(response.status_code, 200)
self.assertContains(response, "texto esperado")
self.assertTemplateUsed(response, "template.html")
```

### 8.7 Boas Práticas

**✅ FAZER:**
- Usar `setUpTestData` para dados compartilhados (mais rápido)
- Usar `setUp` para estado que muda entre testes
- Um teste deve testar UMA funcionalidade
- Testes devem ser independentes (ordem não importa)
- Usar `--keepdb` para testes mais rápidos durante desenvolvimento
- Nomear testes descritivamente (nome deve explicar o que testa)
- Sempre fazer `page.refresh_from_db()` após hooks/signals modificarem dados
- Testar casos de sucesso E casos de erro
- Validar mensagens de erro/sucesso quando aplicável
- **CRÍTICO**: Limpar páginas filhas no `setUpTestData` para evitar conflitos de path
- **CRÍTICO**: Criar `Site` no `setUpTestData` quando testes renderizam templates
- **CRÍTICO**: Adicionar sistema de mensagens ao request mock quando necessário
- **CRÍTICO**: Re-publicar páginas após adicionar tags para queries `.live()`

**❌ EVITAR:**
- Testes que dependem de ordem de execução
- Testes que modificam dados de `setUpTestData`
- Múltiplas asserções não relacionadas no mesmo teste
- Alterar código de produção para fazer teste passar (ajustar o teste!)
- Ignorar warnings e skipped tests sem investigar
- Duplicar código de setup entre arquivos de teste (usar `core.utils_test`)
- Usar `cls.root_page.numchild = 0` (não funciona com `ensure_root_page()` compartilhado)

### 8.8 Coverage e Qualidade

```bash
# Rodar testes com coverage
coverage run --source='.' manage.py test --keepdb

# Ver relatório no terminal
coverage report

# Gerar relatório HTML detalhado
coverage html
# Abrir htmlcov/index.html no navegador

# Rodar testes de um app específico
python manage.py test agenda --keepdb

# Rodar uma classe de teste específica
python manage.py test agenda.test_wagtail_hooks.WagtailHooksTestCase --keepdb

# Rodar um teste específico
python manage.py test agenda.test_wagtail_hooks.WagtailHooksTestCase.test_titulo_com_data --keepdb
```

**Metas de Coverage:**
- Mínimo aceitável: 70%
- Recomendado: 80%+
- Crítico (hooks, APIs, lógica negócio): 90%+

### 8.9 Testes de Integração vs Unitários

**Testes Unitários:**
- Testam uma função/método isoladamente
- Rápidos e focados
- Usam mocks para dependências externas
- Exemplo: testar função `get_titulo_formatado()`

**Testes de Integração:**
- Testam fluxo completo (create → publish → verify)
- Incluem interação entre components
- Verificam comportamento end-to-end
- Exemplo: criar página → hook modifica → publicar → verificar resultado

**Ambos são importantes!** Use testes unitários para helpers e testes de integração para fluxos de usuário.

### 8.10 Exemplo Completo

```python
from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from wagtail.models import Locale, Site
from taggit.models import Tag
from core.utils_test import ensure_root_page
from home.models import HomePage
from eventos.models import EventosPage, EventosIndexPage

class EventosPageTestCase(TestCase):
    """Testes para agenda com recorrência."""
    
    @classmethod
    def setUpTestData(cls):
        """Setup de dados compartilhados."""
        cls.root_page = ensure_root_page()
        
        # CRÍTICO: Limpar páginas filhas para evitar conflitos de path
        for child in cls.root_page.get_children():
            child.delete()
        
        cls.root_page.refresh_from_db()
        cls.locale = Locale.get_default()
        cls.factory = RequestFactory()
        
        # CRÍTICO: Criar Site para testes que renderizam templates
        if not Site.objects.filter(is_default_site=True).exists():
            cls.site = Site.objects.create(
                hostname='localhost',
                port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name='Test Site'
            )
        else:
            cls.site = Site.objects.get(is_default_site=True)
        
        # Criar HomePage
        cls.home_page = HomePage(
            title="Home Test",
            slug="home-test",
        )
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()
        
        # Criar EventosIndexPage
        cls.index_page = EventosIndexPage(
            title="Eventos",
            slug="eventos",
        )
        cls.home_page.add_child(instance=cls.index_page)
        cls.index_page.save_revision().publish()
    
    def setUp(self):
        """Setup por teste."""
        self.root_page.refresh_from_db()
        self.index_page.refresh_from_db()
    
    def test_criar_evento_com_tags(self):
        """CRÍTICO: Republish após adicionar tags para queries .live()."""
        tag = Tag.objects.create(name="Palestra", slug="palestra")
        
        evento = EventosPage(
            title="Evento Palestra",
            slug="evento-palestra",
            descricao="Teste",
        )
        self.index_page.add_child(instance=evento)
        evento.save()
        
        # CRÍTICO: Re-publicar após adicionar tags
        evento.tags.add(tag)
        evento.save_revision().publish()
        
        # Agora queries .live() funcionam corretamente
        posts = EventosPage.objects.live().filter(tags=tag)
        self.assertEqual(posts.count(), 1)
    
    def test_validacao_titulo_longo(self):
        """Validação: add_child() chama full_clean() automaticamente."""
        evento = EventosPage(
            title="A" * 51,  # Maior que o limite
            slug="evento-longo",
            descricao="Teste",
        )
        
        # CRÍTICO: assertRaises deve envolver add_child()
        # porque Wagtail chama full_clean() no save()
        with self.assertRaises(ValidationError) as context:
            self.index_page.add_child(instance=evento)
        
        self.assertIn("title", context.exception.message_dict)
    
    def test_tag_archive_route(self):
        """Teste de rota que renderiza template."""
        tag = Tag.objects.create(name="Palestra", slug="palestra")
        
        evento = EventosPage(
            title="Evento Palestra",
            slug="evento-palestra",
            descricao="Teste",
        )
        self.index_page.add_child(instance=evento)
        evento.save()
        evento.tags.add(tag)
        evento.save_revision().publish()
        
        # CRÍTICO: Adicionar site ao request para templates
        request = self.factory.get(f"{self.index_page.url}tags/palestra/")
        request.site = self.site
        
        response = self.index_page.tag_archive(request, tag="palestra")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Evento Palestra", response.content)
    
    def test_tag_archive_tag_inexistente(self):
        """Teste de rota que usa django.contrib.messages."""
        # CRÍTICO: Adicionar sistema de mensagens ao request mock
        request = self.factory.get(f"{self.index_page.url}tags/inexistente/")
        request.site = self.site
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = self.index_page.tag_archive(request, tag="inexistente")
        self.assertEqual(response.status_code, 302)  # Redirect
```

### 8.11 Checklist de Teste para Nova Feature

- [ ] Testado cenário de sucesso principal
- [ ] Testado casos de erro/exceção
- [ ] Testado condições de contorno (None, vazio, valores extremos)
- [ ] Testado com diferentes locales se aplicável
- [ ] Hooks testados em create E publish
- [ ] Verificado comportamento quando condição desativada
- [ ] Usado `refresh_from_db()` após modificações de hook
- [ ] Mensagens de erro/sucesso validadas
- [ ] Coverage mínimo 70% atingido
- [ ] Todos os testes passando: `python manage.py test <app> --keepdb`

### 8.12 Problemas Comuns e Soluções em Testes

**Problema 1: ValidationError: 'path': ['Página com este Path já existe']**
- **Causa**: Múltiplas classes de teste compartilham `ensure_root_page()` e criam páginas filhas com mesmos slugs
- **Solução**: Limpar páginas filhas no `setUpTestData`:
```python
@classmethod
def setUpTestData(cls):
    cls.root_page = ensure_root_page()
    # CRÍTICO: Limpar filhos antes de criar novos
    for child in cls.root_page.get_children():
        child.delete()
    cls.root_page.refresh_from_db()
```

**Problema 2: IntegrityError: NOT NULL constraint failed**
- **Causa**: Modelo foi alterado mas migration não foi aplicada no banco de testes
- **Solução**: Criar e aplicar migration:
```bash
python manage.py makemigrations <app>
python manage.py migrate
# Ou rodar testes sem --keepdb uma vez
python manage.py test <app>
```

**Problema 3: AssertionError: 0 != 1 ao filtrar por tags**
- **Causa**: Tags adicionadas após `publish()` não aparecem em queries `.live()`
- **Solução**: Re-publicar após adicionar tags:
```python
page.save()
page.tags.add(tag)
page.save_revision().publish()  # CRÍTICO: Re-publicar!
```

**Problema 4: AttributeError: 'NoneType' object has no attribute 'root_page'**
- **Causa**: Template usa `{% get_site_root %}` mas request não tem Site
- **Solução**: Criar Site e adicionar ao request:
```python
@classmethod
def setUpTestData(cls):
    if not Site.objects.filter(is_default_site=True).exists():
        cls.site = Site.objects.create(
            hostname='localhost',
            port=80,
            root_page=cls.root_page,
            is_default_site=True,
            site_name='Test Site'
        )
    else:
        cls.site = Site.objects.get(is_default_site=True)

def test_meu_teste(self):
    request = self.factory.get('/path/')
    request.site = self.site  # Adicionar site
```

**Problema 5: MessageFailure: You cannot add messages without installing middleware**
- **Causa**: View usa `messages.add_message()` mas request mock não tem sistema de mensagens
- **Solução**: Adicionar FallbackStorage ao request:
```python
from django.contrib.messages.storage.fallback import FallbackStorage

request = self.factory.get('/path/')
setattr(request, 'session', {})
messages = FallbackStorage(request)
setattr(request, '_messages', messages)
```

**Problema 6: ValidationError não é capturado por assertRaises**
- **Causa**: `add_child()` chama `save()` que chama `full_clean()` automaticamente
- **Solução**: assertRaises deve envolver add_child():
```python
# ❌ ERRADO
page.add_child(instance=child)
with self.assertRaises(ValidationError):
    child.clean()

# ✅ CORRETO
with self.assertRaises(ValidationError):
    page.add_child(instance=child)
```

## 9. Fluxo de Trabalho

### 8.11 Checklist de Teste para Nova Feature

- [ ] Testado cenário de sucesso principal
- [ ] Testado casos de erro/exceção
- [ ] Testado condições de contorno (None, vazio, valores extremos)
- [ ] Testado com diferentes locales se aplicável
- [ ] Hooks testados em create E publish
- [ ] Verificado comportamento quando condição desativada
- [ ] Usado `refresh_from_db()` após modificações de hook
- [ ] Mensagens de erro/sucesso validadas
- [ ] Coverage mínimo 70% atingido
- [ ] Todos os testes passando: `python manage.py test <app> --keepdb`

## 9. Fluxo de Trabalho

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

## 10. Lições Aprendidas - Casos Reais de Debugging

### 10.1 Criação de Testes para Apps com Wagtail (Nov 2025)

**Contexto**: Criação de 49 testes para apps `eventos` (20 testes) e `avisos` (29 testes)

**Problemas Encontrados e Soluções Aplicadas:**

1. **Conflitos de Path em Testes Paralelos** (49 erros iniciais)
   - Sintoma: `ValidationError: 'path': ['Página com este Path já existe']`
   - Causa Raiz: `ensure_root_page()` retorna a MESMA root_page para todas as classes de teste. Quando múltiplas classes criam filhos com mesmos slugs, há conflito.
   - ❌ Solução Tentada (Falhou): Alterar slugs para serem únicos entre classes
   - ✅ Solução Correta: Limpar páginas filhas no `setUpTestData`:
   ```python
   @classmethod
   def setUpTestData(cls):
       cls.root_page = ensure_root_page()
       # CRÍTICO: Limpar ANTES de criar novas
       for child in cls.root_page.get_children():
           child.delete()
       cls.root_page.refresh_from_db()
   ```
   - **Lição**: `ensure_root_page()` é compartilhado entre TODOS os testes. Sempre limpar estado anterior.

2. **Campo Removido mas Migration Não Aplicada** (18 erros)
   - Sintoma: `IntegrityError: NOT NULL constraint failed: eventos_eventospage.subtitle`
   - Causa Raiz: Campo `subtitle` foi removido do modelo mas migration não foi criada/aplicada
   - ✅ Solução:
   ```bash
   python manage.py makemigrations eventos
   # Criou: eventos/migrations/0005_remove_eventospage_subtitle.py
   python manage.py migrate
   ```
   - **Lição**: Sempre criar migrations para alterações de modelo, MESMO em ambiente de testes.

3. **Tags Adicionadas Após Publicação Não Aparecem** (4 falhas)
   - Sintoma: `AssertionError: 0 != 1` ao filtrar por tags
   - Causa Raiz: Wagtail `.live()` queries retornam apenas revisões publicadas. Tags adicionadas após `publish()` ficam apenas no draft.
   - ❌ Padrão Incorreto:
   ```python
   page.save_revision().publish()
   page.tags.add(tag)  # Tag vai para draft, não para live
   posts = Page.objects.live().filter(tags=tag)  # 0 resultados
   ```
   - ✅ Padrão Correto:
   ```python
   page.save()
   page.tags.add(tag)
   page.save_revision().publish()  # Re-publicar após tags
   posts = Page.objects.live().filter(tags=tag)  # Funciona!
   ```
   - **Lição**: Sempre re-publicar após modificar campos relacionados (tags, images, etc.) se precisar consultar via `.live()`.

4. **Validações Django em Testes** (2 erros)
   - Sintoma: `ValidationError` lançado fora do `assertRaises`
   - Causa Raiz: Wagtail chama `full_clean()` automaticamente no `save()` dentro de `add_child()`
   - ❌ Padrão Incorreto:
   ```python
   page.add_child(instance=child)  # ValidationError aqui!
   with self.assertRaises(ValidationError):
       child.clean()  # Nunca executado
   ```
   - ✅ Padrão Correto:
   ```python
   with self.assertRaises(ValidationError):
       page.add_child(instance=child)  # Captura erro
   ```
   - **Lição**: `add_child()` → `save()` → `full_clean()` automático. Envolver a operação completa no `assertRaises`.

5. **Templates Renderizados em Testes Precisam de Site** (4 erros)
   - Sintoma: `AttributeError: 'NoneType' object has no attribute 'root_page'`
   - Causa Raiz: Template usa `{% get_site_root %}` que precisa de `Site.find_for_request(request)`
   - ✅ Solução:
   ```python
   @classmethod
   def setUpTestData(cls):
       # Criar Site
       if not Site.objects.filter(is_default_site=True).exists():
           cls.site = Site.objects.create(
               hostname='localhost',
               port=80,
               root_page=cls.root_page,
               is_default_site=True,
               site_name='Test Site'
           )
   
   def test_route(self):
       request = self.factory.get('/url/')
       request.site = self.site  # CRÍTICO
       response = self.page.route_method(request)
   ```
   - **Lição**: Testes que renderizam templates Wagtail precisam de Site configurado no request.

6. **Django Messages em Request Mock** (2 erros)
   - Sintoma: `MessageFailure: You cannot add messages without installing middleware`
   - Causa Raiz: View usa `messages.add_message()` mas `RequestFactory` não inclui sistema de mensagens
   - ✅ Solução:
   ```python
   from django.contrib.messages.storage.fallback import FallbackStorage
   
   request = self.factory.get('/url/')
   setattr(request, 'session', {})
   messages = FallbackStorage(request)
   setattr(request, '_messages', messages)
   ```
   - **Lição**: Mock de request precisa de session e messages storage para views que usam `django.contrib.messages`.

**Progressão de Erros Durante Debug:**
- Inicial: 49 erros (path conflicts)
- Após limpeza de páginas: 18 erros (migration faltando)
- Após migration: 4 falhas + 6 erros (tags + validações + site + messages)
- Após fixes completos: **0 erros, 0 falhas, 49 testes passando** ✅

**Imports Necessários para Testes Completos:**
```python
from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from django.contrib.messages.storage.fallback import FallbackStorage
from wagtail.models import Page, Locale, Site
from taggit.models import Tag
from core.utils_test import ensure_root_page
```

## 11. Observações Importantes

1. **SEMPRE** verificar duplicação de código antes de criar nova função
2. **NUNCA** criar documentação markdown sem perguntar ao usuário
3. **SEMPRE** criar testes para novas funcionalidades
4. **SEMPRE** usar `ensure_root_page()` de `core.utils_test` em testes
5. **SEMPRE** normalizar locale 'pt-br' → 'pt' em testes Wagtail
6. **CRÍTICO**: Limpar páginas filhas no `setUpTestData` quando usar `ensure_root_page()`
7. **SEMPRE** fazer `root.refresh_from_db()` após operações de página
8. Usar `RenameField` para preservar dados em migrations
9. Verificar conflitos de nomes entre classes pai/filho
10. Perguntar sobre documentação antes de gerar
11. **SEMPRE** perguntar sobre comandos de ambiente antes de executar pela primeira vez
12. **CRÍTICO**: Re-publicar páginas após adicionar tags/relacionamentos para queries `.live()`
13. **CRÍTICO**: Criar `Site` no `setUpTestData` quando testes renderizam templates

## 12. Contato e Suporte

- Projeto: Site Padrão CODATA-PB
- Stack: Django 5.1 + Wagtail 7.x + PostgreSQL
- Python: 3.12+
- Configurações de ambiente: veja `.github/copilot-local.md`
