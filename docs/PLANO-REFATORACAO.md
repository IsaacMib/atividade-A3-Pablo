# 🎯 PLANO DE REFATORAÇÃO - NeuroPrev Multimodal
**Gerado**: 24 de novembro de 2025  
**Baseado em**: AUDITORIA-PROJETO.md

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Fase 1: Limpeza Crítica](#fase-1-limpeza-crítica-2-3-dias)
3. [Fase 2: Frontend](#fase-2-frontend-2-3-dias)
4. [Fase 3: Templates](#fase-3-templates-2-dias)
5. [Fase 4: Homepage StreamField](#fase-4-homepage-streamfield-1-dia)
6. [Fase 5: Reorganização Apps](#fase-5-reorganização-apps-2-3-dias)
7. [Fase 6: Fixtures](#fase-6-fixtures-1-2-dias)
8. [Fase 7: Validação](#fase-7-validação-1-dia)
9. [Fase 8: Documentação](#fase-8-documentação-1-dia)
10. [Infraestrutura (Opcional)](#infraestrutura-opcional)

---

## 📊 VISÃO GERAL

### Objetivo
Transformar codebase de "Site Padrão CODATA (portal governamental)" → **NeuroPrev Multimodal (plataforma de triagem de autismo)** profissional e manutenível.

### Status Atual
- ✅ **IA Multimodal**: 16/16 tarefas concluídas
- ✅ **Testes**: 45/45 passando (96% coverage)
- ❌ **Código Legado**: 35+ referências a remover
- ❌ **Homepage**: 136 linhas hardcoded
- ❌ **Inline Code**: 2 scripts no base.html

### Impacto Esperado
- **Redução de código**: ~5.000 linhas removidas
- **Manutenibilidade**: +300%
- **Onboarding**: -70% tempo para novos devs
- **Performance**: Bundle JS/CSS otimizado
- **SEO**: Melhor semântica e estrutura

### Duração Total Estimada
**12-16 dias úteis** (2-3 semanas)

---

## 🚨 FASE 1: LIMPEZA CRÍTICA (2-3 dias)

### Objetivo
Remover completamente código relacionado a portal governamental que não tem relação com triagem de autismo.

---

### ✅ Tarefa 1.1: Remover Período Eleitoral (4h)

**Por quê?** Lei eleitoral brasileira não se aplica a sistema de triagem de autismo.

#### Arquivos a modificar:

**1. core/models.py** (4 alterações)
```python
# REMOVER linhas 356-371
periodo_eleitoral_habilitado = models.BooleanField(...)
periodo_eleitoral_inicio = models.DateField(...)
periodo_eleitoral_fim = models.DateField(...)
texto_informativo_periodo_eleitoral = models.TextField(...)

# REMOVER linhas 502-505 (FieldPanel)
FieldPanel("periodo_eleitoral_habilitado"),
FieldPanel("periodo_eleitoral_inicio"),
FieldPanel("periodo_eleitoral_fim"),
FieldPanel("texto_informativo_periodo_eleitoral"),

# REMOVER linhas 564-573 (método)
def is_periodo_eleitoral(self):
    ...

# REMOVER linhas 621-622 (validação clean)
if self.periodo_eleitoral_habilitado:
    if not self.periodo_eleitoral_inicio or not self.periodo_eleitoral_fim:
```

**2. Criar migration**
```bash
python manage.py makemigrations core --name remove_periodo_eleitoral
# Migration vai gerar RemoveField para os 4 campos
python manage.py migrate
```

**3. Buscar outras referências**
```bash
grep -r "periodo_eleitoral" --include="*.py" --include="*.html"
# Remover todas as referências encontradas
```

#### Validação:
```bash
python manage.py check
pytest core/tests/ --cov -v
# Todos os testes devem passar
```

---

### ✅ Tarefa 1.2: Remover Sistema Intranet (3h)

**Por quê?** Sistema de triagem é para responsáveis/profissionais, não é intranet governamental.

#### Arquivos a modificar (15 referências):

**1. sitepadrao/settings/base.py**
```python
# REMOVER linha 358
HABILITAR_SITE_INTRANET = get_bool("HABILITAR_SITE_INTRANET", False)
```

**2. sitepadrao/context_processors.py**
```python
# REMOVER linha 7
"HABILITAR_SITE_INTRANET": getattr(settings, 'HABILITAR_SITE_INTRANET', False),
```

**3. sitepadrao/urls.py**
```python
# REMOVER linhas 46-48
if settings.HABILITAR_SITE_INTRANET:
    urlpatterns += [path("intranet/", include("intranet.urls"))]
```

**4. sitepadrao/templates/header.html**
```django
{# REMOVER linhas 7 e 71 #}
{% if HABILITAR_SITE_INTRANET %}
  {% include 'include/perfil.html' %}
{% endif %}
```

**5. core/templates/tags/top_menu.html**
```django
{# REMOVER linhas 32 e 136 - condicionais #}
{% if HABILITAR_SITE_INTRANET %}
  {% include 'include/perfil.html' %}
{% endif %}
```

**6. core/templatetags/navigation_tags.py**
```python
# REMOVER linha 75
"HABILITAR_SITE_INTRANET": context.get("HABILITAR_SITE_INTRANET", False),
```

**7. blocks/models.py**
```python
# REMOVER linha 516
if getattr(settings, 'HABILITAR_SITE_INTRANET', False):
    ...
```

**8. core/templates/include/perfil.html**
```html
<!-- RENOMEAR classes CSS -->
<div class="header-user-icon-wrapper">  <!-- era header-intranet-user-icon-wrapper -->
  <div class="header-user-icon">        <!-- era header-intranet-user-icon -->
```

**9. .env.example**
```bash
# REMOVER linha 262
# HABILITAR_SITE_INTRANET=False
```

**10. Buscar CSS relacionado**
```bash
grep -r "header-intranet" frontend/scss/
# Se encontrar: renomear para header-user
```

#### Validação:
```bash
python manage.py check
python manage.py runserver
# Testar navegação completa no navegador
# Verificar menu, perfil de usuário, breadcrumb
pytest --cov -v
```

---

### ✅ Tarefa 1.3: Limpar Referências CODATA (2h)

**Por quê?** Projeto foi reestruturado para NeuroPrev, referências antigas confundem.

#### Busca global:
```bash
grep -ri "codata" --include="*.py" --include="*.html" --include="*.md" --exclude-dir=docs
```

#### Arquivos a verificar:
```
test_integration.py linha 12  - Atualizar import se necessário
core/templatetags/           - Verificar referências
sitepadrao/templates/        - Buscar "CODATA" em comentários
README.md                    - Atualizar se menciona CODATA
```

#### Ação:
- **Manter**: docs/LIMPEZA-REFERENCIAS.md, docs/REESTRUTURACAO.md (histórico)
- **Remover/Substituir**: Todas as outras por "NeuroPrev"

#### Validação:
```bash
grep -ri "codata" . --exclude-dir=docs --exclude-dir=.git
# Resultado deve ser vazio ou apenas comentários OK
```

---

### ✅ Tarefa 1.4: Avaliar Apps Duvidosos (4h)

#### Apps a investigar:

**1. dicas_presidente/**
```bash
# Verificar
grep -r "dicas_presidente" --include="*.py"
ls -la dicas_presidente/
# Se não usado: REMOVER
```

**2. paginas_codata/**
```bash
# Verificar
grep -r "paginas_codata" --include="*.py"
# Provavelmente legado CODATA - REMOVER
```

**3. plone_migration/**
```bash
# Verificar se migration foi concluída
ls -la plone_migration/
grep -r "plone_migration" --include="*.py"
# Se migration completa: REMOVER
```

**4. tw/**
```bash
# Identificar propósito
grep -r "tw" --include="*.py" | head -20
# Se não usado: REMOVER
```

**5. triagem/ (antigo) vs triagem_ia/ (novo)**
```bash
# Verificar qual é usado
grep -r "from triagem " --include="*.py"
grep -r "from triagem_ia " --include="*.py"
# Comparar models, verificar dados no DB
# Se triagem/ não é usado: REMOVER
```

#### Processo de remoção de app:
```python
# 1. Remover de INSTALLED_APPS (settings/base.py)
# 2. Remover imports em outros arquivos
# 3. Remover de urls.py se registrado
# 4. Criar migration para remover tabelas
python manage.py makemigrations --empty app_removido
# Na migration: operations = [migrations.RunSQL("DROP TABLE IF EXISTS app_model;")]
# 5. Deletar pasta do app
rm -rf app_removido/
# 6. Rodar testes
pytest --cov -v
```

---

### 📊 Checkpoint Fase 1

**Antes de prosseguir, verificar:**
- [ ] `python manage.py check` passa
- [ ] `pytest --cov -v` passa (manter 96%+)
- [ ] `python manage.py runserver` inicia sem erros
- [ ] Navegação no browser funciona (menu, páginas)
- [ ] Commit: `git commit -m "refactor: remover código legado (período eleitoral, intranet, CODATA)"`

**Resultado esperado:**
- ✅ ~35+ referências legado removidas
- ✅ 4 campos + 1 método removidos do SiteSettings
- ✅ 15 condicionais intranet removidas
- ✅ 1-5 apps removidos (dependendo da análise)

---

## 🎨 FASE 2: FRONTEND (2-3 dias)

### Objetivo
Remover código inline, organizar static files, modularizar JavaScript.

---

### ✅ Tarefa 2.1: Extrair Google Analytics Inline (2h)

#### Arquivo: `frontend/js/analytics.js` (criar)
```javascript
/**
 * Google Analytics Setup
 * Carregado condicionalmente se tem_google_analytics=True
 */

// Verificar se GA_MEASUREMENT_ID está definido
if (typeof GA_MEASUREMENT_ID !== 'undefined' && GA_MEASUREMENT_ID) {
    // Criar script tag para gtag.js
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    document.head.appendChild(script);

    // Inicializar dataLayer
    window.dataLayer = window.dataLayer || [];
    function gtag() {
        dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', GA_MEASUREMENT_ID);

    console.log('[Analytics] Google Analytics carregado');
} else {
    console.log('[Analytics] GA_MEASUREMENT_ID não definido');
}
```

#### Modificar: `sitepadrao/templates/base.html`
```django
<!-- REMOVER linhas 82-89 (inline script) -->

<!-- ADICIONAR antes de </body> -->
{% if settings.core.SiteSettings.tem_google_analytics %}
  <script>
    const GA_MEASUREMENT_ID = "{{ settings.core.SiteSettings.google_analytics_codigo }}";
  </script>
  <script src="{% static 'js/analytics.js' %}"></script>
{% endif %}
```

#### Atualizar webpack se necessário:
```javascript
// webpack.config.js
entry: {
  main: './frontend/js/index.js',
  analytics: './frontend/js/analytics.js',  // Se precisar de bundle separado
}
```

#### Validação:
```bash
npm run build
python manage.py runserver
# Abrir DevTools → Network → Verificar analytics.js carrega
# Abrir DevTools → Console → Verificar log "[Analytics]"
```

---

### ✅ Tarefa 2.2: Extrair VLibras Widget Inline (1h)

#### Arquivo: `frontend/js/vlibras.js` (criar)
```javascript
/**
 * VLibras Accessibility Widget
 * https://www.gov.br/governodigital/pt-br/vlibras
 */

(function() {
    // Criar script do plugin VLibras
    const script = document.createElement('script');
    script.src = 'https://vlibras.gov.br/app/vlibras-plugin.js';
    script.onload = function() {
        // Inicializar widget após carregar
        new window.VLibras.Widget('https://vlibras.gov.br/app');
        console.log('[VLibras] Widget carregado');
    };
    document.head.appendChild(script);
})();
```

#### Modificar: `sitepadrao/templates/base.html`
```django
<!-- REMOVER linhas 95-98 (inline script VLibras) -->

<!-- ADICIONAR antes de </body> -->
<div vw class="enabled">
    <div vw-access-button class="active"></div>
    <div vw-plugin-wrapper></div>
</div>
<script src="{% static 'js/vlibras.js' %}"></script>
```

#### Validação:
```bash
npm run build
python manage.py collectstatic --noinput
python manage.py runserver
# Verificar botão VLibras aparece no canto inferior direito
# Clicar e testar tradução para Libras
```

---

### ✅ Tarefa 2.3: Buscar e Remover CSS Inline (3h)

#### Scan completo:
```bash
# Buscar style="..." em templates
grep -rn 'style="' --include="*.html" sitepadrao/ core/ blocks/ home/ noticias/

# Buscar <style> tags
grep -rn '<style>' --include="*.html" sitepadrao/ core/ blocks/ home/ noticias/
```

#### Para cada ocorrência:
1. **Identificar padrão** (cor, padding, margin, display, etc.)
2. **Criar classe SCSS** seguindo BEM:
   ```scss
   // Exemplo: home_page.html hero section
   .hero-section {
       background: linear-gradient(135deg, $color-primary 0%, $color-primary-darker 100%);
       color: $color-on-primary;
       padding: 80px 20px;
       text-align: center;
   }
   ```
3. **Substituir inline por classe**:
   ```html
   <!-- Antes -->
   <section style="background: linear-gradient(...); color: white; padding: 80px 20px;">
   
   <!-- Depois -->
   <section class="hero-section">
   ```
4. **Testar responsividade** (mobile, tablet, desktop)

#### Arquivos SCSS a criar/modificar:
```
frontend/scss/home/homepage_blocks.scss        # Novos blocos homepage
frontend/scss/home/homepage_blocks_escuro.scss # Tema escuro
frontend/scss/blocks/feature_card.scss         # Cards de features
frontend/scss/sitepadrao/cta.scss              # Call-to-action
```

#### Validação:
```bash
npm run build
# Verificar no browser: visual idêntico ao anterior
# Testar tema escuro: alternar e verificar cores
# Testar responsivo: mobile, tablet, desktop
```

---

### ✅ Tarefa 2.4: Auditar Assets Órfãos (2h)

#### Listar imagens:
```bash
find frontend/img -type f > frontend_images.txt
find sitepadrao/static/img -type f > static_images.txt
```

#### Para cada imagem, buscar referências:
```bash
while read img; do
  filename=$(basename "$img")
  refs=$(grep -r "$filename" --include="*.html" --include="*.scss" --include="*.js" --include="*.py" | wc -l)
  if [ $refs -eq 0 ]; then
    echo "ÓRFÃO: $img"
  fi
done < frontend_images.txt
```

#### Remover imagens órfãs:
```bash
# Criar backup antes
tar -czf frontend_img_backup.tar.gz frontend/img/

# Deletar imagens não referenciadas
# (Manualmente ou com script)
```

#### Validação:
```bash
npm run build
python manage.py collectstatic
# Verificar no browser: todas as imagens carregam
# Verificar console: sem 404 de imagens
```

---

### 📊 Checkpoint Fase 2

**Antes de prosseguir, verificar:**
- [ ] `npm run build` passa sem erros
- [ ] `python manage.py collectstatic --noinput` passa
- [ ] Google Analytics funciona (se habilitado)
- [ ] VLibras widget aparece e funciona
- [ ] Sem `style="..."` em templates HTML
- [ ] Todas as imagens carregam (sem 404)
- [ ] Commit: `git commit -m "refactor: modularizar frontend (extrair inline, limpar assets)"`

**Resultado esperado:**
- ✅ 0 scripts inline
- ✅ 0 estilos inline (ou <5 se absolutamente necessário)
- ✅ 2 arquivos JS novos (analytics.js, vlibras.js)
- ✅ ~10-20 classes SCSS criadas
- ✅ Assets órfãos removidos

---

## 📄 FASE 3: TEMPLATES (2 dias)

### Objetivo
Reorganizar templates seguindo padrões Wagtail, eliminar duplicação, criar partials reutilizáveis.

---

### ✅ Tarefa 3.1: Criar Estrutura de Pastas (1h)

#### Criar pastas:
```bash
cd sitepadrao/templates/
mkdir -p partials/navigation partials/meta partials/social errors pages
```

#### Estrutura final:
```
sitepadrao/templates/
  base.html                # Template base global
  partials/                # ✨ NOVO - Componentes reutilizáveis
    header.html
    footer.html
    breadcrumbs.html
    navigation/
      top_menu.html        # Mover de core/templates/tags/
      mobile_menu.html     # ✨ NOVO - Extrair de top_menu
      dropdown_item.html   # ✨ NOVO - Extrair de top_menu
    meta/
      seo_meta.html        # ✨ NOVO - Meta tags SEO
      og_tags.html         # ✨ NOVO - Open Graph
    social/
      sharing.html         # Mover de core/templates/tags/compartilhamento
  errors/                  # ✨ NOVO - Templates de erro
    403.html
    404.html
    500.html
    503.html
    erro_base.html
  pages/                   # ✨ NOVO - Templates de páginas específicas
    (futuros templates)
```

---

### ✅ Tarefa 3.2: Mover e Renomear Templates (2h)

#### 1. Mover templates de erro:
```bash
mv 403.html 404.html 500.html 503.html erro_base.html errors/
```

#### 2. Mover header e footer:
```bash
mv header.html footer.html partials/
```

#### 3. Mover breadcrumb:
```bash
mv include/breadcrumb.html partials/breadcrumbs.html
```

#### 4. Mover top_menu:
```bash
mv ../core/templates/tags/top_menu.html partials/navigation/
```

#### 5. Mover compartilhamento:
```bash
mv ../core/templates/tags/compartilhamento.html partials/social/sharing.html
```

#### 6. Atualizar base.html:
```django
{# Antes #}
{% include 'header.html' %}
{% include 'include/breadcrumb.html' %}
{% include 'footer.html' %}

{# Depois #}
{% include 'partials/header.html' %}
{% include 'partials/breadcrumbs.html' %}
{% include 'partials/footer.html' %}
```

---

### ✅ Tarefa 3.3: Quebrar top_menu em Componentes (3h)

**Problema**: top_menu.html tem 148 linhas, difícil de manter.

#### Análise:
```django
{# top_menu.html atual #}
<nav>
  <!-- Desktop menu (linhas 1-80) -->
  <div class="navbar-desktop">
    {% for item in menu_items %}
      <!-- Dropdown complexo com submenus -->
    {% endfor %}
  </div>
  
  <!-- Mobile menu (linhas 81-130) -->
  <div class="navbar-mobile">
    <!-- Accordion Bootstrap -->
  </div>
  
  <!-- User profile (linhas 131-148) -->
  {% include 'include/perfil.html' %}
</nav>
```

#### Criar: `partials/navigation/desktop_menu.html`
```django
{# Apenas menu desktop #}
<div class="navbar-desktop d-none d-lg-block">
  {% for item in menu_items %}
    {% include 'partials/navigation/menu_item.html' with item=item %}
  {% endfor %}
</div>
```

#### Criar: `partials/navigation/mobile_menu.html`
```django
{# Apenas menu mobile #}
<div class="navbar-mobile d-lg-none">
  <div class="accordion" id="mobileMenuAccordion">
    {% for item in menu_items %}
      {% include 'partials/navigation/accordion_item.html' with item=item %}
    {% endfor %}
  </div>
</div>
```

#### Criar: `partials/navigation/menu_item.html`
```django
{# Item de menu (desktop) com dropdown #}
<li class="nav-item {% if item.children %}dropdown{% endif %}">
  <a class="nav-link" href="{{ item.url }}">{{ item.title }}</a>
  {% if item.children %}
    <ul class="dropdown-menu">
      {% for child in item.children %}
        <li><a class="dropdown-item" href="{{ child.url }}">{{ child.title }}</a></li>
      {% endfor %}
    </ul>
  {% endif %}
</li>
```

#### Criar: `partials/navigation/accordion_item.html`
```django
{# Item de menu (mobile) accordion #}
<div class="accordion-item">
  <h2 class="accordion-header">
    <button class="accordion-button" data-bs-toggle="collapse" data-bs-target="#menu-{{ item.id }}">
      {{ item.title }}
    </button>
  </h2>
  <div id="menu-{{ item.id }}" class="accordion-collapse collapse">
    <div class="accordion-body">
      {% for child in item.children %}
        <a href="{{ child.url }}" class="d-block py-2">{{ child.title }}</a>
      {% endfor %}
    </div>
  </div>
</div>
```

#### Atualizar: `partials/navigation/top_menu.html` (novo)
```django
{# Arquivo principal - apenas orquestra componentes #}
<nav class="navbar navbar-expand-lg">
  <div class="container">
    {% include 'partials/navigation/desktop_menu.html' %}
    {% include 'partials/navigation/mobile_menu.html' %}
    {% include 'partials/user_profile.html' %}  {# era include/perfil.html #}
  </div>
</nav>
```

---

### ✅ Tarefa 3.4: Criar Partials SEO (2h)

#### Criar: `partials/meta/seo_meta.html`
```django
{# Meta tags SEO #}
{% load wagtailcore_tags wagtailimages_tags %}

<meta name="description" content="{{ page.search_description|default:page.descricao|truncatewords:30 }}">
<meta name="keywords" content="{{ page.seo_keywords|default:'' }}">
<meta name="author" content="NeuroPrev">

{% if page.get_imagem_destaque %}
  {% image page.get_imagem_destaque fill-1200x630 as og_image %}
  <meta property="og:image" content="{{ request.scheme }}://{{ request.get_host }}{{ og_image.url }}">
{% endif %}

<link rel="canonical" href="{{ page.full_url }}">
```

#### Criar: `partials/meta/og_tags.html`
```django
{# Open Graph tags para redes sociais #}
<meta property="og:type" content="website">
<meta property="og:title" content="{{ page.seo_title|default:page.title }}">
<meta property="og:description" content="{{ page.search_description|default:page.descricao|truncatewords:30 }}">
<meta property="og:url" content="{{ page.full_url }}">
<meta property="og:site_name" content="NeuroPrev Multimodal">

{# Twitter Card #}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ page.seo_title|default:page.title }}">
<meta name="twitter:description" content="{{ page.search_description|default:page.descricao|truncatewords:30 }}">
```

#### Adicionar ao base.html `<head>`:
```django
<head>
  {# ... charset, viewport, etc ... #}
  
  {% block meta %}
    {% include 'partials/meta/seo_meta.html' %}
    {% include 'partials/meta/og_tags.html' %}
  {% endblock meta %}
  
  {# ... resto do head ... #}
</head>
```

---

### ✅ Tarefa 3.5: Eliminar Duplicação (2h)

#### Caso 1: Headers de notícias

**Analisar duplicação:**
```bash
diff noticias/templates/include/header-noticia.html noticias/templates/include/header-index.html
```

**Se forem muito similares:**
```django
{# Criar: partials/page_header.html (genérico) #}
<header class="page-header">
  {% if image %}
    {% include 'partials/header_with_image.html' %}
  {% else %}
    {% include 'partials/header_simple.html' %}
  {% endif %}
</header>
```

#### Caso 2: Títulos de blocos

**Verificar:**
```
blocks/templates/include/titulo.html
blocks/templates/blocks/titulo.html
```

**Se duplicados: unificar em um só arquivo**

---

### 📊 Checkpoint Fase 3

**Antes de prosseguir, verificar:**
- [ ] Estrutura de pastas criada corretamente
- [ ] Todos `{% include %}` atualizados
- [ ] `python manage.py check` passa
- [ ] `python manage.py runserver` inicia
- [ ] Navegação no browser funciona (menu, breadcrumb)
- [ ] Páginas carregam sem erros 404 de templates
- [ ] Commit: `git commit -m "refactor: reorganizar templates (partials, navegação modular)"`

**Resultado esperado:**
- ✅ Estrutura `partials/`, `errors/`, `pages/` criada
- ✅ top_menu.html quebrado em 5 componentes
- ✅ Partials SEO criados (meta, og_tags)
- ✅ Duplicação reduzida em ~30%
- ✅ Templates 50% mais legíveis

---

## 🏠 FASE 4: HOMEPAGE STREAMFIELD (1 dia)

### Objetivo
Converter homepage de 136 linhas hardcoded → 100% editável via Wagtail admin com 4 blocks.

---

### ✅ Tarefa 4.1: Criar Blocks Home (3h)

#### Arquivo: `blocks/home.py` (criar novo)
```python
"""
Blocks específicos para Homepage
"""
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeroBlock(blocks.StructBlock):
    """Banner hero da homepage com gradiente"""
    
    titulo = blocks.CharBlock(
        label="Título Principal",
        max_length=100,
        help_text="Ex: NeuroPrev"
    )
    
    subtitulo = blocks.CharBlock(
        label="Subtítulo",
        max_length=200,
        help_text="Ex: Sistema Multimodal de Triagem Precoce para TEA"
    )
    
    descricao = blocks.TextBlock(
        label="Descrição",
        max_length=500,
        help_text="Texto explicativo sob o subtítulo"
    )
    
    botao_primario = blocks.StructBlock([
        ('texto', blocks.CharBlock(label="Texto", max_length=50)),
        ('url', blocks.URLBlock(label="URL")),
    ], label="Botão Primário")
    
    botao_secundario = blocks.StructBlock([
        ('texto', blocks.CharBlock(label="Texto", max_length=50, required=False)),
        ('url', blocks.URLBlock(label="URL", required=False)),
    ], label="Botão Secundário (Opcional)", required=False)
    
    imagem_fundo = ImageChooserBlock(
        label="Imagem de Fundo",
        required=False,
        help_text="Se não definida, usa gradiente padrão"
    )
    
    class Meta:
        template = "blocks/hero_home.html"
        icon = "image"
        label = "Hero Banner"


class FeatureCardBlock(blocks.StructBlock):
    """Card individual de feature/recurso"""
    
    icone = blocks.CharBlock(
        label="Ícone (Emoji)",
        max_length=10,
        help_text="Ex: 🧠 🔒 📊"
    )
    
    titulo = blocks.CharBlock(
        label="Título",
        max_length=100
    )
    
    descricao = blocks.TextBlock(
        label="Descrição",
        max_length=300
    )
    
    class Meta:
        template = "blocks/feature_card.html"
        icon = "doc-full"
        label = "Feature Card"


class FeaturesGridBlock(blocks.StructBlock):
    """Grid de features (2 ou 3 colunas)"""
    
    titulo_secao = blocks.CharBlock(
        label="Título da Seção",
        max_length=100,
        help_text="Ex: Recursos Principais"
    )
    
    features = blocks.ListBlock(
        FeatureCardBlock(),
        min_num=2,
        max_num=6,
        label="Features"
    )
    
    colunas = blocks.ChoiceBlock(
        label="Número de Colunas",
        choices=[
            ('2', 'Duas Colunas'),
            ('3', 'Três Colunas'),
        ],
        default='3'
    )
    
    class Meta:
        template = "blocks/features_grid.html"
        icon = "grip"
        label = "Grid de Features"


class CTABlock(blocks.StructBlock):
    """Call-to-Action simples"""
    
    titulo = blocks.CharBlock(
        label="Título",
        max_length=100
    )
    
    descricao = blocks.TextBlock(
        label="Descrição",
        max_length=400
    )
    
    botao = blocks.StructBlock([
        ('texto', blocks.CharBlock(label="Texto", max_length=50)),
        ('url', blocks.URLBlock(label="URL")),
    ], label="Botão")
    
    estilo = blocks.ChoiceBlock(
        label="Estilo do CTA",
        choices=[
            ('primary', 'Primário (Gradiente Roxo)'),
            ('secondary', 'Secundário (Branco)'),
        ],
        default='primary'
    )
    
    class Meta:
        template = "blocks/cta_home.html"
        icon = "arrow-right"
        label = "Call to Action"
```

#### Registrar no HomePage:
```python
# home/models.py

from blocks.home import HeroBlock, FeaturesGridBlock, CTABlock

class HomePage(Page):
    body = StreamField(
        [
            ("hero", HeroBlock()),
            ("features_grid", FeaturesGridBlock()),
            ("cta", CTABlock()),
            # Blocks existentes
            ("banner", blocks.CarrosselBannersBlock()),
            ("video", blocks.VideoBlock()),
            # ...
        ],
        blank=True,
        use_json_field=True,
    )
    
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
```

---

### ✅ Tarefa 4.2: Criar Templates de Blocks (2h)

#### Template: `blocks/templates/blocks/hero_home.html`
```django
{% load wagtailcore_tags wagtailimages_tags static %}

<section class="hero-home">
  {% if value.imagem_fundo %}
    {% image value.imagem_fundo fill-1920x1080 as hero_bg %}
    <div class="hero-home__background" style="background-image: url('{{ hero_bg.url }}');"></div>
  {% else %}
    <div class="hero-home__background hero-home__background--gradient"></div>
  {% endif %}
  
  <div class="container hero-home__content">
    <h1 class="hero-home__title">{{ value.titulo }}</h1>
    <p class="hero-home__subtitle">{{ value.subtitulo }}</p>
    <p class="hero-home__description">{{ value.descricao }}</p>
    
    <div class="hero-home__actions">
      <a href="{{ value.botao_primario.url }}" class="btn btn-hero btn-hero--primary">
        {{ value.botao_primario.texto }}
      </a>
      
      {% if value.botao_secundario.texto %}
        <a href="{{ value.botao_secundario.url }}" class="btn btn-hero btn-hero--secondary">
          {{ value.botao_secundario.texto }}
        </a>
      {% endif %}
    </div>
  </div>
</section>
```

#### Template: `blocks/templates/blocks/feature_card.html`
```django
<div class="feature-card">
  <div class="feature-card__icon">{{ value.icone }}</div>
  <h3 class="feature-card__title">{{ value.titulo }}</h3>
  <p class="feature-card__description">{{ value.descricao }}</p>
</div>
```

#### Template: `blocks/templates/blocks/features_grid.html`
```django
{% load wagtailcore_tags %}

<section class="features-grid">
  <div class="container">
    <h2 class="features-grid__title">{{ value.titulo_secao }}</h2>
    
    <div class="features-grid__items features-grid__items--cols-{{ value.colunas }}">
      {% for feature in value.features %}
        {% include_block feature %}
      {% endfor %}
    </div>
  </div>
</section>
```

#### Template: `blocks/templates/blocks/cta_home.html`
```django
<section class="cta-home cta-home--{{ value.estilo }}">
  <div class="container cta-home__content">
    <h2 class="cta-home__title">{{ value.titulo }}</h2>
    <p class="cta-home__description">{{ value.descricao }}</p>
    <a href="{{ value.botao.url }}" class="btn btn-cta btn-cta--{{ value.estilo }}">
      {{ value.botao.texto }}
    </a>
  </div>
</section>
```

---

### ✅ Tarefa 4.3: Criar SCSS dos Blocks (2h)

#### Arquivo: `frontend/scss/home/homepage_blocks.scss`
```scss
@use '../variables.scss' as *;

// Hero Home
.hero-home {
  position: relative;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  
  &__background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    z-index: 0;
    
    &--gradient {
      background: linear-gradient(135deg, $color-primary 0%, $color-primary-darker 100%);
    }
  }
  
  &__content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: $color-on-primary;
    padding: 80px 20px;
  }
  
  &__title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    
    @media (max-width: 768px) {
      font-size: 2rem;
    }
  }
  
  &__subtitle {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    opacity: 0.95;
    
    @media (max-width: 768px) {
      font-size: 1.2rem;
    }
  }
  
  &__description {
    font-size: 1.2rem;
    margin-bottom: 2.5rem;
    opacity: 0.85;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    
    @media (max-width: 768px) {
      font-size: 1rem;
    }
  }
  
  &__actions {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }
}

.btn-hero {
  padding: 15px 40px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.2s;
  
  &--primary {
    background: $color-white;
    color: $color-primary;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
  }
  
  &--secondary {
    background: rgba($color-white, 0.2);
    color: $color-white;
    border: 2px solid $color-white;
    
    &:hover {
      background: rgba($color-white, 0.3);
    }
  }
}

// Features Grid
.features-grid {
  padding: 80px 20px;
  background: $color-grey-100;
  
  &__title {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 60px;
    color: $color-grey-900;
  }
  
  &__items {
    display: grid;
    gap: 40px;
    
    &--cols-2 {
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    }
    
    &--cols-3 {
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
}

.feature-card {
  background: $color-white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }
  
  &__icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, $color-primary 0%, $color-primary-darker 100%);
    border-radius: 50%;
    margin: 0 auto 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
  }
  
  &__title {
    font-size: 1.5rem;
    margin-bottom: 15px;
    color: $color-grey-900;
  }
  
  &__description {
    color: $color-grey-700;
    line-height: 1.6;
  }
}

// CTA Home
.cta-home {
  padding: 80px 20px;
  text-align: center;
  
  &--primary {
    background: $color-white;
  }
  
  &--secondary {
    background: $color-grey-100;
  }
  
  &__content {
    max-width: 800px;
    margin: 0 auto;
  }
  
  &__title {
    font-size: 2.5rem;
    margin-bottom: 25px;
    color: $color-grey-900;
  }
  
  &__description {
    font-size: 1.2rem;
    color: $color-grey-700;
    margin-bottom: 35px;
    line-height: 1.6;
  }
}

.btn-cta {
  padding: 15px 40px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  display: inline-block;
  transition: all 0.2s;
  
  &--primary {
    background: linear-gradient(135deg, $color-primary 0%, $color-primary-darker 100%);
    color: $color-on-primary;
    box-shadow: 0 4px 15px rgba($color-primary, 0.4);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba($color-primary, 0.5);
    }
  }
  
  &--secondary {
    background: $color-white;
    color: $color-primary;
    border: 2px solid $color-primary;
    
    &:hover {
      background: $color-primary;
      color: $color-on-primary;
    }
  }
}
```

#### Arquivo: `frontend/scss/home/homepage_blocks_escuro.scss`
```scss
@use '../variables.scss' as *;

[data-theme="dark"] {
  .hero-home {
    &__background--gradient {
      // Gradiente mais escuro para tema dark
      background: linear-gradient(135deg, darken($color-primary, 15%) 0%, darken($color-primary-darker, 15%) 100%);
    }
  }
  
  .features-grid {
    background: $color-dark-theme-bg;
    
    &__title {
      color: $color-dark-theme-text;
    }
  }
  
  .feature-card {
    background: $color-dark-theme-surface;
    
    &__title {
      color: $color-dark-theme-text;
    }
    
    &__description {
      color: $color-dark-theme-text-secondary;
    }
  }
  
  .cta-home {
    &--primary {
      background: $color-dark-theme-surface;
    }
    
    &--secondary {
      background: $color-dark-theme-bg;
    }
    
    &__title {
      color: $color-dark-theme-text;
    }
    
    &__description {
      color: $color-dark-theme-text-secondary;
    }
  }
}
```

#### Adicionar ao main.scss:
```scss
// frontend/scss/main.scss
@use './home/homepage_blocks';
@use './home/homepage_blocks_escuro';
```

---

### ✅ Tarefa 4.4: Popular Homepage via Admin (1h)

#### Passos:
1. Compilar frontend: `npm run build`
2. Rodar servidor: `python manage.py runserver`
3. Acessar Wagtail admin: `/cms/`
4. Editar HomePage
5. Adicionar blocks na ordem:
   - **HeroBlock**:
     - Título: "NeuroPrev"
     - Subtítulo: "Sistema Multimodal de Triagem Precoce para TEA"
     - Descrição: "Detecção precoce... IA..."
     - Botão 1: "Acessar Painel" → "/painel/"
     - Botão 2: "Admin Wagtail" → "/cms/"
   
   - **FeaturesGridBlock**:
     - Título: "Recursos Principais"
     - Colunas: 3
     - Features (adicionar 6):
       1. 🧠 Triagem Multimodal | Análise integrada...
       2. 📊 Painel Diário | Registro e acompanhamento...
       3. 👥 Comunidade | Espaço para troca...
       4. 📚 Biblioteca | Material educativo...
       5. 🔒 LGPD | Proteção de dados...
       6. 🤖 IA Multimodal | Análise por IA...
   
   - **CTABlock**:
     - Título: "Comece agora"
     - Descrição: "Faça o cadastro e inicie a triagem..."
     - Botão: "Criar Conta" → "/accounts/signup/"
     - Estilo: primary

6. Salvar e publicar
7. Visualizar no frontend: `/`

---

### ✅ Tarefa 4.5: Remover Hardcoded do Template (30min)

#### Modificar: `home/templates/home/home_page.html`
```django
{% extends "base.html" %}
{% load static wagtailcore_tags %}

{% block body_class %}template-homepage{% endblock %}

{% block content %}
  {% if page.body %}
    {% for block in page.body %}
      {% include_block block %}
    {% endfor %}
  {% else %}
    {# REMOVER TODO O BLOCO {% else %} (linhas 13-143) #}
    {# Agora sempre use blocks do admin #}
    <section class="hero-home">
      <div class="hero-home__background hero-home__background--gradient"></div>
      <div class="container hero-home__content">
        <h1 class="hero-home__title">Configure a Homepage</h1>
        <p class="hero-home__subtitle">Adicione blocks via Wagtail Admin</p>
        <div class="hero-home__actions">
          <a href="/cms/pages/{{ page.id }}/edit/" class="btn btn-hero btn-hero--primary">
            Editar Homepage
          </a>
        </div>
      </div>
    </section>
  {% endif %}
{% endblock content %}
```

---

### 📊 Checkpoint Fase 4

**Antes de prosseguir, verificar:**
- [ ] Blocks criados em `blocks/home.py`
- [ ] 4 templates de blocks criados
- [ ] SCSS compilado sem erros: `npm run build`
- [ ] HomePage populada via admin com 3 blocks
- [ ] Visual idêntico ao anterior (ou melhor)
- [ ] Tema escuro funcionando
- [ ] Responsivo: mobile, tablet, desktop
- [ ] Commit: `git commit -m "feat: homepage 100% StreamField com 4 blocks editáveis"`

**Resultado esperado:**
- ✅ 0 linhas hardcoded na homepage
- ✅ 100% editável via Wagtail admin
- ✅ 4 blocks novos (Hero, Features, CTA)
- ✅ ~200 linhas de SCSS organizado
- ✅ Editor de conteúdo pode mudar homepage sem código

---

## 📁 FASE 5: REORGANIZAÇÃO APPS (2-3 dias)

(... continua com detalhes de verificação de apps, remoção, migrations, etc ...)

---

## 🌱 FASE 6: FIXTURES (1-2 dias)

(... continua com criação de management commands, factories, população automática ...)

---

## ✅ FASE 7: VALIDAÇÃO (1 dia)

(... continua com checks Django, testes, validação manual, correção de erros ...)

---

## 📚 FASE 8: DOCUMENTAÇÃO (1 dia)

(... continua com atualização README, criação de guias técnicos ...)

---

## 🐘 INFRAESTRUTURA (OPCIONAL)

### PostgreSQL Setup
(... continua com instalação, configuração, migração de dados ...)

### Celery + Redis Setup
(... continua com instalação, configuração, testes async ...)

---

## 🎉 CONCLUSÃO

Após completar todas as 8 fases, o projeto estará:

✅ **Limpo** - Sem código legado de portal governamental  
✅ **Organizado** - Estrutura clara e manutenível  
✅ **Moderno** - Frontend modularizado, sem inline code  
✅ **Editável** - Homepage e conteúdo via Wagtail admin  
✅ **Documentado** - Guias para novos desenvolvedores  
✅ **Testado** - 96%+ coverage mantido  
✅ **Profissional** - Pronto para produção

**Próximos passos sugeridos:**
1. Setup de staging environment
2. CI/CD com GitLab pipelines
3. Monitoramento (Sentry, logs)
4. Backup automatizado
5. Performance optimization (caching, CDN)

---

**Última atualização**: 24 de novembro de 2025
