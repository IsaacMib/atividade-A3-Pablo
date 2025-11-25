# 🏗️ Nova Estrutura de Apps - NEUROATHENA

**Data**: 25 de novembro de 2025  
**Padrão**: Cada página institucional = 1 App Django

---

## 📋 Mudanças Implementadas

### ✅ Migração de Arquitetura

**ANTES** (tudo em `home/models.py`):
```
home/
└── models.py
    ├── HomePage
    ├── SobreNosPage
    ├── ParaFamiliasPage
    ├── ParaProfissionaisPage
    ├── IAMultimodalPage
    └── ContatoPage
```

**DEPOIS** (apps separados):
```
sobre_nos/
├── models.py (SobreNosPage + subpáginas)
├── migrations/
└── templates/

para_familias/
├── models.py (ParaFamiliasPage + subpáginas)
├── migrations/
└── templates/

para_profissionais/
├── models.py (ParaProfissionaisPage + subpáginas)
├── migrations/
└── templates/

ia_multimodal/
├── models.py (IAMultimodalPage + subpáginas)
├── migrations/
└── templates/

contato/
├── models.py (ContatoPage + FormField)
├── migrations/
└── templates/

home/
└── models.py (APENAS HomePage)
```

---

## 📦 Apps Criados

### 1. **sobre_nos/** - Sobre Nós

**Models** (5):
- `SobreNosPage` - Página principal
- `MissaoVisaoPage` - Missão, Visão, Valores
- `EquipePage` - Equipe técnica (index)
- `MembroEquipePage` - Membro individual
- `ParceriasPage` - Parcerias institucionais

**Hierarquia**:
```
HomePage
└── SobreNosPage
    ├── MissaoVisaoPage
    ├── EquipePage
    │   └── MembroEquipePage (vários)
    └── ParceriasPage
```

---

### 2. **para_familias/** - Para Famílias

**Models** (6):
- `ParaFamiliasPage` - Página principal
- `ComoFuncionaPage` - Como funciona a triagem
- `RecursosEducativosPage` - Recursos educativos (index)
- `RecursoEducativoPage` - Recurso individual (artigo, guia, vídeo)
- `HistoriasSucessoPage` - Histórias de sucesso (index)
- `HistoriaSucessoPage` - História individual

**Hierarquia**:
```
HomePage
└── ParaFamiliasPage
    ├── ComoFuncionaPage
    ├── RecursosEducativosPage
    │   └── RecursoEducativoPage (vários)
    └── HistoriasSucessoPage
        └── HistoriaSucessoPage (vários)
```

**Campos customizados**:
- `RecursoEducativoPage.tipo_recurso` (artigo, guia, vídeo, infográfico)
- `HistoriaSucessoPage.nome_familia` (opcional/anônimo)

---

### 3. **para_profissionais/** - Para Profissionais

**Models** (5):
- `ParaProfissionaisPage` - Página principal
- `SuiteClinicaPage` - Suíte clínica
- `APIDocumentacaoPage` - Documentação API
- `EstudosValidacaoPage` - Estudos científicos (index)
- `EstudoCientificoPage` - Estudo individual

**Hierarquia**:
```
HomePage
└── ParaProfissionaisPage
    ├── SuiteClinicaPage
    ├── APIDocumentacaoPage
    └── EstudosValidacaoPage
        └── EstudoCientificoPage (vários)
```

**Campos customizados**:
- `EstudoCientificoPage.autores`
- `EstudoCientificoPage.publicacao`
- `EstudoCientificoPage.ano`
- `EstudoCientificoPage.doi`

---

### 4. **ia_multimodal/** - IA Multimodal Athena

**Models** (6):
- `IAMultimodalPage` - Página principal
- `ModuloVideoPage` - Análise de vídeo (facial)
- `ModuloAudioPage` - Análise de áudio (prosódia)
- `ModuloTextoPage` - Análise de texto (linguagem)
- `FusaoMultimodalPage` - Fusão multimodal (CLIP, ImageBind)
- `EticaPrivacidadePage` - Ética e privacidade

**Hierarquia**:
```
HomePage
└── IAMultimodalPage
    ├── ModuloVideoPage
    ├── ModuloAudioPage
    ├── ModuloTextoPage
    ├── FusaoMultimodalPage
    └── EticaPrivacidadePage
```

---

### 5. **contato/** - Contato

**Models** (2):
- `ContatoPage` - Formulário de contato (AbstractEmailForm)
- `FormField` - Campos customizados do formulário

**Hierarquia**:
```
HomePage
└── ContatoPage (sem filhas)
```

**Campos customizados**:
- `email_contato` - Email institucional
- `telefone`
- `endereco`
- `horario_atendimento`
- `intro` - Texto introdutório (RichText)
- `thank_you_text` - Texto de agradecimento (RichText)

---

## 📊 Comparação com App `institucional`

Seguimos o padrão do app **`institucional/`** existente:

| Característica | institucional/ | Novos Apps |
|----------------|----------------|------------|
| Herança base | `PageSitePadrao` | `PageNeuroAthena` ✅ |
| `parent_page_types` | ✅ Definido | ✅ Definido |
| `subpage_types` | ✅ Definido | ✅ Definido |
| Hierarquia de páginas | ✅ Index → Grupo → Página | ✅ Principal → Subpáginas |
| StreamField blocks | ✅ Custom blocks | ✅ Blocos de `blocks/blocks.py` |
| Templates separados | ✅ `templates/` | ✅ `templates/` (a criar) |
| Campos customizados | ✅ Sim | ✅ Sim (cargo, tipo_recurso, etc.) |

---

## 🎯 Benefícios da Nova Estrutura

### ✅ Organização
- Cada app é **auto-contido** (models, views, templates, migrations)
- Fácil navegar e encontrar código relacionado
- Escalável: adicionar novo app não afeta existentes

### ✅ Manutenibilidade
- Mudanças em "Para Famílias" não afetam "Para Profissionais"
- Migrations separadas por app
- Testes isolados por funcionalidade

### ✅ Colaboração
- Desenvolvedores podem trabalhar em apps diferentes simultaneamente
- Menos conflitos de merge no Git
- Responsabilidades claras por área

### ✅ Deploy
- Pode desabilitar um app sem quebrar outros
- Migrations aplicadas incrementalmente
- Rollback mais seguro

### ✅ Reutilização
- Apps podem ser reutilizados em outros projetos Django/Wagtail
- Blocks compartilhados via `blocks/blocks.py`
- Base comum via `core.models.PageNeuroAthena`

---

## 🔧 Configuração Técnica

### INSTALLED_APPS (settings/base.py)

```python
INSTALLED_APPS = [
    # Apps institucionais (Fase 1)
    "sobre_nos",           # ✅ Sobre Nós
    "para_familias",       # ✅ Para Famílias
    "para_profissionais",  # ✅ Para Profissionais
    "ia_multimodal",       # ✅ IA Multimodal
    "contato",             # ✅ Contato
    
    # Apps do NEUROATHENA
    "triagem_ia",          # Triagem (área logada)
    "painel_diario",       # Painel Diário
    "comunidade",          # Comunidade
    
    # Apps base
    "home",
    "core",
    "blocks",
    "noticias",
    # ...
]
```

### Migrations Criadas

```bash
✅ contato/migrations/0001_initial.py
   - ContatoPage
   - FormField

✅ ia_multimodal/migrations/0001_initial.py
   - IAMultimodalPage
   - ModuloVideoPage
   - ModuloAudioPage
   - ModuloTextoPage
   - FusaoMultimodalPage
   - EticaPrivacidadePage

✅ para_familias/migrations/0001_initial.py
   - ParaFamiliasPage
   - ComoFuncionaPage
   - RecursosEducativosPage
   - RecursoEducativoPage
   - HistoriasSucessoPage
   - HistoriaSucessoPage

✅ para_profissionais/migrations/0001_initial.py
   - ParaProfissionaisPage
   - SuiteClinicaPage
   - APIDocumentacaoPage
   - EstudosValidacaoPage
   - EstudoCientificoPage

✅ sobre_nos/migrations/0001_initial.py
   - SobreNosPage
   - MissaoVisaoPage
   - EquipePage
   - MembroEquipePage
   - ParceriasPage

✅ home/migrations/0004_remove_...
   - Removidos models duplicados (movidos para apps específicos)
```

### Verificação

```bash
python manage.py check
# System check identified no issues (0 silenced). ✅
```

---

## 📝 Total de Models por App

| App | Models | Total |
|-----|--------|-------|
| sobre_nos | SobreNosPage, MissaoVisaoPage, EquipePage, MembroEquipePage, ParceriasPage | 5 |
| para_familias | ParaFamiliasPage, ComoFuncionaPage, RecursosEducativosPage, RecursoEducativoPage, HistoriasSucessoPage, HistoriaSucessoPage | 6 |
| para_profissionais | ParaProfissionaisPage, SuiteClinicaPage, APIDocumentacaoPage, EstudosValidacaoPage, EstudoCientificoPage | 5 |
| ia_multimodal | IAMultimodalPage, ModuloVideoPage, ModuloAudioPage, ModuloTextoPage, FusaoMultimodalPage, EticaPrivacidadePage | 6 |
| contato | ContatoPage, FormField | 2 |
| **TOTAL** | | **24 models** |

---

## 🚀 Próximos Passos

### Fase 2 - Templates HTML

Criar templates em cada app:
```
sobre_nos/templates/sobre_nos/
├── sobre_nos_page.html
├── missao_visao_page.html
├── equipe_page.html
├── membro_equipe_page.html
└── parcerias_page.html

para_familias/templates/para_familias/
├── para_familias_page.html
├── como_funciona_page.html
├── recursos_educativos_page.html
├── recurso_educativo_page.html
├── historias_sucesso_page.html
└── historia_sucesso_page.html

# ... (outros apps)
```

### Fase 3 - Popular Conteúdo

Via admin do Wagtail:
1. Criar `SobreNosPage` como filha de `HomePage`
2. Adicionar subpáginas (`MissaoVisaoPage`, `EquipePage`, etc.)
3. Marcar "Show in menus" para navegação
4. Adicionar conteúdo usando StreamField blocks

---

## 📚 Documentação Relacionada

- [FASE_1_COMPLETA.md](./FASE_1_COMPLETA.md) - Checklist da Fase 1
- [03_ARQUITETURA/estrutura_site.md](./03_ARQUITETURA/estrutura_site.md) - Estrutura completa do site
- [Estrutura.md](./Estrutura.md) - Planejamento original

---

**Gerado em**: 25/11/2025  
**Status**: ✅ Implementado e testado com sucesso
