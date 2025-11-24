# Limpeza de Referências ao Portal Antigo

## Data: Dezembro 2024
## Objetivo: Remover referências ao "Site Padrão CODATA" e substituir por "NeuroPrev Multimodal"

---

## ✅ Arquivos Atualizados

### 1. Configurações Python

#### `core/models.py`
```python
# ANTES:
title_suffix = models.CharField(
    default="Site Padrão",
    help_text="Título do site e utilizado como sufixo na tag meta. Ex.: ' | Site Padrão'",
)

# DEPOIS:
title_suffix = models.CharField(
    default="NeuroPrev",
    help_text="Título do site e utilizado como sufixo na tag meta. Ex.: ' | NeuroPrev'",
)
```

**Ação Necessária:** Criar migration:
```bash
python manage.py makemigrations core -m "atualizar_title_suffix_neuroprev"
python manage.py migrate
```

### 2. Documentação

#### `.github/copilot-instructions.md`
- **Linha 1:** `# Instruções do GitHub Copilot para Site Padrão CODATA` → `# Instruções do GitHub Copilot para NeuroPrev Multimodal`
- **Linha 4:** Descrição alterada de "portais governamentais padronizados" → "triagem precoce de autismo com IA multimodal"
- **Seção 12:** Projeto: `Site Padrão CODATA-PB` → `NeuroPrev Multimodal - Sistema de Triagem de Autismo`

### 3. Templates Django

#### `sitepadrao/templates/footer.html`
- **Linhas 40-67:** Logo CODATA comentado com `{% comment %}`
- **Linhas 70-234:** Logo Governo da Paraíba comentado com `{% comment %}`
- **Adicionado:** TODO para adicionar logo NeuroPrev

#### `sitepadrao/templates/barra_identidade.html`
- **Todo o arquivo comentado:** Barra de identidade do Governo da Paraíba (143 linhas)
- **Motivo:** Componente específico do portal governamental, não relevante para NeuroPrev
- **Adicionado:** Cabeçalho explicativo sobre a remoção

#### `sitepadrao/templates/wagtailadmin/base.html`
- **Logo CODATA comentado:** `logo-codata.svg` não será mais exibido
- **Substituído por:** `<h2>{{ WAGTAIL_SITE_NAME }}</h2>` (NeuroPrev Multimodal)
- **Adicionado:** Subtítulo com `{{ settings.core.SiteSettings.title_suffix }}`

---

## 🔍 Referências NÃO Alteradas (Por Design)

### Migrations do Django
- **Localização:** `core/migrations/`, `home/migrations/`
- **Motivo:** Migrations são histórico de banco de dados e NÃO devem ser modificadas
- **Exemplo:** `0001_initial.py` com `default='Site Padrão'` permanece intacto

### Documentação Histórica
- `docs/REESTRUTURACAO.md` - Documento histórico da reestruturação
- `docs/RENOMEACAO.md` - Explica mudança de nome
- `docs/STATUS.md` - Status do projeto durante transição

### JavaScript de Terceiros
- `frontend/js/barraidentidadepb/barraidentidadepb.js` - Biblioteca externa
  - Não modificada pois pode ser removida completamente no futuro
  - Mantida apenas para compatibilidade temporária

---

## 📋 Próximas Etapas Recomendadas

### Imediato
1. ✅ **Criar migration para `core.models.SiteSettings.title_suffix`**
   ```bash
   python manage.py makemigrations core -m "atualizar_title_suffix_neuroprev"
   python manage.py migrate
   ```

2. ✅ **Testar templates atualizados**
   ```bash
   python manage.py runserver
   # Acessar: http://localhost:8000
   # Verificar: Footer sem logos governamentais
   # Verificar: Admin Wagtail com título "NeuroPrev Multimodal"
   ```

### Médio Prazo (Fase 2 - Identidade Visual)

3. **Criar logo NeuroPrev**
   - Formato: SVG (escalável)
   - Localização: `frontend/img/logo-neuroprev.svg`
   - Descomentar e atualizar em:
     * `sitepadrao/templates/footer.html`
     * `sitepadrao/templates/wagtailadmin/base.html`

4. **Criar favicon NeuroPrev**
   - Formatos: `.ico`, `.png` (múltiplos tamanhos)
   - Substituir `frontend/img/favicon/*`

5. **Atualizar CSS/SCSS**
   - Remover classes específicas do governo (`.orgao-barra`, `.barra-brasil`, etc.)
   - Criar nova paleta de cores NeuroPrev
   - Atualizar `frontend/scss/variables.scss`

### Longo Prazo (Fase 3 - Remoção Completa)

6. **Remover arquivos não utilizados**
   ```bash
   # Listar para revisão antes de deletar
   frontend/js/barraidentidadepb/
   frontend/img/logo-codata.svg
   frontend/img/logo_sic.png
   ```

7. **Limpar banco de dados de teste**
   ```bash
   # Remover dados de exemplo do portal antigo
   python manage.py shell
   # >>> SiteSettings.objects.update(title_suffix="NeuroPrev")
   ```

---

## 🎨 Design Guidelines NeuroPrev

### Paleta de Cores Sugerida (Autismo)
```scss
// Cores Autismo Awareness
$neuroprev-primary: #00A3E0;      // Azul quebra-cabeça
$neuroprev-secondary: #7FC241;    // Verde esperança
$neuroprev-accent: #FFB81C;       // Amarelo atenção
$neuroprev-dark: #003B5C;         // Azul escuro
$neuroprev-light: #E8F5FA;        // Azul claro fundo
```

### Tipografia
- **Títulos:** Fonte sem-serifa moderna (ex: Inter, Roboto)
- **Corpo:** Fonte legível para pais/cuidadores (ex: Open Sans)
- **Acessibilidade:** Contraste mínimo 4.5:1 (WCAG AA)

### Logo Concept
- **Elemento Visual:** Quebra-cabeça (símbolo autismo) + Cérebro estilizado
- **Texto:** "NeuroPrev" em fonte amigável
- **Slogan:** "Triagem Precoce com IA Multimodal"

---

## ✅ Checklist de Validação

- [x] `core/models.py` atualizado
- [x] `.github/copilot-instructions.md` atualizado
- [x] `footer.html` logos comentados
- [x] `barra_identidade.html` completamente comentado
- [x] `wagtailadmin/base.html` logo removido
- [ ] Migration criada e aplicada
- [ ] Templates testados visualmente
- [ ] Logo NeuroPrev criado
- [ ] Favicon atualizado
- [ ] CSS/SCSS atualizado
- [ ] Arquivos antigos removidos

---

## 📝 Notas Importantes

### Por que não deletar imediatamente?

1. **Migrations:** Nunca deletar - são histórico de banco de dados
2. **Templates comentados:** Permitem recuperar estrutura se necessário durante desenvolvimento
3. **JavaScript externo:** Pode ter dependências não óbvias - comentar antes de deletar

### Impacto nos Usuários

- **Desenvolvedores:** Precisarão rodar nova migration
- **Usuários finais:** Verão novo nome "NeuroPrev" ao invés de "Site Padrão"
- **Admin Wagtail:** Interface administrativa mostrará "NeuroPrev Multimodal"

### Reversão (Se necessário)

Para reverter as mudanças:
```bash
git revert HEAD~3  # Reverter últimos 3 commits
# OU
git checkout main -- <arquivo>  # Reverter arquivo específico
```

---

**Criado em:** Dezembro 2024  
**Autor:** GitHub Copilot + Desenvolvedor  
**Status:** ✅ Concluído - Aguardando migration
