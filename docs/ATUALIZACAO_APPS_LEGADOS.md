# ✅ Atualização Apps Legados - PageNeuroAthena

**Data**: 25 de novembro de 2025  
**Ação**: Migração de `PageSitePadrao` → `PageNeuroAthena`

---

## 📦 Apps Atualizados

### 1. **paginas/** - Páginas Genéricas Reutilizáveis

**Models abstratos atualizados** (5):
- `CorpoTecnicoIndexPage` - Base para índice de corpo técnico
- `CorpoTecnicoGrupoPageIndex` - Base para grupos de corpo técnico
- `CorpoTecnicoPage` - Base para membros individuais
- `RichTextPage` - Página de texto rico genérica
- `PaginaComBannerPage` - Página com banner e introdução

**Models concretos** (1):
- `RedirectPage` - Página de redirecionamento (interno/externo)

**Alterações realizadas**:
```python
# ANTES
from core.models import PageSitePadrao, PageSitePadraoIndex

class CorpoTecnicoIndexPage(PageSitePadraoIndex):
    content_panels = PageSitePadraoIndex.content_panels + [...]

# DEPOIS
from core.models import PageNeuroAthena, PageNeuroAthenaIndex

class CorpoTecnicoIndexPage(PageNeuroAthenaIndex):
    content_panels = PageNeuroAthenaIndex.content_panels + [...]
```

**Total de alterações**: 11 substituições (imports + 5 classes + 5 content_panels)

---

### 2. **institucional/** - Páginas Institucionais Legadas

**Models atualizados** (7):
- `InstitucionalIndexPage` - Índice institucional
- `LocalizacaoPage` - Página de localizações
- `SecretariadoIndex` - Índice do secretariado (herda de `CorpoTecnicoIndexPage`)
- `SecretariadoGrupoPageIndex` - Grupos do secretariado
- `SecretariadoPage` - Membros do secretariado
- `ComiteDeEticaPage` - Comitê de ética (herda de `PaginaComBannerPage`)
- `AEmpresaPage` - A Empresa (herda de `RichTextPage`)
- `MissaoVisaoValores` - Missão, Visão, Valores (herda de `PaginaComBannerPage`)

**Alterações realizadas**:
```python
# ANTES
from core.models import PageSitePadrao, PageSitePadraoIndex

class InstitucionalIndexPage(PageSitePadraoIndex):
    ...

class LocalizacaoPage(PageSitePadrao):
    content_panels = PageSitePadrao.content_panels + [...]

# DEPOIS
from core.models import PageNeuroAthena, PageNeuroAthenaIndex

class InstitucionalIndexPage(PageNeuroAthenaIndex):
    ...

class LocalizacaoPage(PageNeuroAthena):
    content_panels = PageNeuroAthena.content_panels + [...]
```

**Total de alterações**: 4 substituições (import + 2 classes + 1 content_panel)

---

## 🔄 Hierarquia de Herança Atualizada

### Páginas Base (abstratas em paginas/)

```
PageNeuroAthenaIndex (core.models)
├── CorpoTecnicoIndexPage (abstrata)
│   └── SecretariadoIndex (institucional)
└── CorpoTecnicoGrupoPageIndex (abstrata)
    └── SecretariadoGrupoPageIndex (institucional)

PageNeuroAthena (core.models)
├── CorpoTecnicoPage (abstrata)
│   └── SecretariadoPage (institucional)
├── RichTextPage (abstrata)
│   └── AEmpresaPage (institucional)
├── PaginaComBannerPage (abstrata)
│   ├── ComiteDeEticaPage (institucional)
│   └── MissaoVisaoValores (institucional)
└── RedirectPage (concreta)
```

### Páginas Institucionais (institucional/)

```
HomePage
└── InstitucionalIndexPage
    ├── LocalizacaoPage
    ├── SecretariadoIndex
    │   └── SecretariadoGrupoPageIndex
    │       └── SecretariadoPage (vários)
    ├── ComiteDeEticaPage
    ├── AEmpresaPage
    └── MissaoVisaoValores
```

---

## 🎯 Por que PageNeuroAthena?

### Benefícios da Migração:

1. **Consistência de Nomenclatura**
   - Padrão unificado: "NEUROATHENA" em toda aplicação
   - Remove referência ao antigo "SitePadrao"

2. **Campos Herdados Automaticamente**
   - `descricao` (TextField) - Descrição da página
   - `imagem_destaque` (ForeignKey para Image) - Imagem de destaque
   - `get_imagem_destaque()` - Método helper para obter imagem

3. **Reutilização de Código**
   - Classes abstratas em `paginas/` usadas por `institucional/`
   - Evita duplicação de models

4. **Compatibilidade com Novos Apps**
   - `sobre_nos`, `para_familias`, `para_profissionais`, etc. já usam `PageNeuroAthena`
   - Padrão unificado facilita manutenção

---

## 📊 Resumo de Alterações

| Arquivo | Models Afetados | Alterações |
|---------|----------------|------------|
| `paginas/models.py` | 6 (5 abstratos + 1 concreto) | 11 substituições |
| `institucional/models.py` | 7 concretos | 4 substituições |
| **TOTAL** | **13 models** | **15 substituições** |

---

## 🔧 Migrations Aplicadas

```bash
✅ institucional/migrations/
   - 0001_initial.py (já existia)
   - 0002_secretariadogrupopageindex_and_more.py (já existia)
   - 0003_alter_secretariadoindex_grupos_corpo_tecnico.py (já existia)
   - 0004_comitedeeticapage.py (já existia)
   - 0005_alter_comitedeeticapage_descricao_and_more.py (já existia)
   - 0006_aempresapage.py (já existia)
   - 0007_missaovisaovalores.py (já existia)

✅ paginas/migrations/
   - 0001_initial.py (NOVO - RedirectPage)
```

**Verificação**:
```bash
python manage.py check
# System check identified no issues (0 silenced). ✅
```

---

## 🆕 Apps Adicionados ao INSTALLED_APPS

```python
# neuroathena/settings/base.py

INSTALLED_APPS = [
    # Apps institucionais (Fase 1)
    "sobre_nos",
    "para_familias",
    "para_profissionais",
    "ia_multimodal",
    "contato",
    
    # ✅ Apps auxiliares/genéricos (ADICIONADOS)
    "paginas",             # Páginas genéricas reutilizáveis
    "institucional",       # Páginas institucionais legadas
    
    # Apps do NEUROATHENA
    "triagem_ia",
    "painel_diario",
    # ...
]
```

---

## 📚 Estrutura Completa de Apps Institucionais

### Apps Novos (Fase 1)
- `sobre_nos/` - Sobre Nós, Missão, Equipe, Parcerias
- `para_familias/` - Para Famílias, Recursos, Histórias
- `para_profissionais/` - Para Profissionais, Suíte Clínica, API
- `ia_multimodal/` - IA Multimodal, Módulos, Ética
- `contato/` - Contato, Formulário

### Apps Auxiliares (Reutilizáveis)
- `paginas/` - Classes abstratas base (CorpoTecnico, RichText, Banner, Redirect)
- `institucional/` - Páginas institucionais legadas (Secretariado, Comitê, Localização)

### Apps Base
- `home/` - HomePage
- `core/` - PageNeuroAthena (base), SiteSettings, utils
- `blocks/` - StreamField blocks reutilizáveis

---

## ✅ Status Final

- ✅ **15 substituições** realizadas (PageSitePadrao → PageNeuroAthena)
- ✅ **13 models** atualizados em 2 apps
- ✅ **2 apps adicionados** ao INSTALLED_APPS
- ✅ **Migrations aplicadas** sem erros
- ✅ **`python manage.py check`** → 0 issues
- ✅ **Padrão unificado** em todo o projeto

---

## 🚀 Próximos Passos

### Fase 2 - Templates
Criar templates para os novos apps institucionais:
- `sobre_nos/templates/sobre_nos/`
- `para_familias/templates/para_familias/`
- `para_profissionais/templates/para_profissionais/`
- `ia_multimodal/templates/ia_multimodal/`
- `contato/templates/contato/`

### Verificar Templates Legados
Os templates em `paginas/templates/paginas/` e `institucional/templates/institucional/` já existem e devem continuar funcionando normalmente.

---

**Gerado em**: 25/11/2025  
**Verificado**: Sistema sem erros ✅
