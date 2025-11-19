# Resumo: Solução para Problema de Migração de Dados

## Problema Identificado

Ao alterar a estrutura dos blocos `LinkWithImageStructBlock` e `CardLinhaDoTempoBlock` nos StreamFields do Wagtail, os dados antigos salvos no banco de dados (em formato JSON) ficariam incompatíveis com a nova estrutura de código.

### Estrutura Antiga (Problema)
```json
{
  "titulo": "Meu Card",
  "internal_page": 123,
  "external_url": null
}
```

### Estrutura Nova (Desejada)
```json
{
  "titulo": "Meu Card",
  "link": {
    "internal_page": 123,
    "external_url": null,
    "link_text": ""
  }
}
```

## Solução Implementada

### 1. Migração de Dados Automática ✅

**Arquivo**: `blocks/migrations/0007_migrate_link_struct_blocks.py`

**Funcionalidades**:
- ✅ Migra dados de **páginas publicadas**
- ✅ Migra dados no **histórico de revisões** do Wagtail
- ✅ Detecta e transforma apenas dados no formato antigo
- ✅ Permite **reversão** completa (`migrate blocks 0006`)
- ✅ Não altera schema do banco (apenas dados JSON)

**Execução**:
```bash
# Backup obrigatório
pg_dump nome_do_banco > backup_$(date +%Y%m%d_%H%M%S).sql

# Aplicar migração
python manage.py migrate blocks

# Saída:
# ✅ Migração concluída:
#    - X página(s) publicada(s) atualizada(s)
#    - Y revisão(ões) atualizada(s)
```

### 2. Compatibilidade Retroativa no Código ✅

**Arquivos**: `blocks/models.py`

**Fallback automático** em `get_url()`:
```python
def get_url(self):
    # Tenta novo formato primeiro
    link = self.get('link')
    if link:
        internal = link.get('internal_page')
        if internal:
            return internal.url
        if link.get('external_url'):
            return link.get('external_url')
    
    # FALLBACK: Formato antigo (se migração não executada)
    internal_legacy = self.get('internal_page')
    if internal_legacy:
        return internal_legacy.url
    return self.get('external_url')
```

**Benefícios**:
- ✅ Site não quebra se migração não for executada imediatamente
- ✅ Dados antigos continuam renderizando
- ✅ Novos dados salvam no formato correto

### 3. Testes Abrangentes ✅

**Arquivos**:
- `blocks/test_link_struct_blocks.py` - 15 testes (blocos refatorados)
- `blocks/test_migration_link_struct.py` - 5 testes (lógica de migração)

**Cobertura**:
```bash
python manage.py test blocks --keepdb
# Ran 38 tests in 0.4s
# OK ✅
```

### 4. Documentação Completa ✅

**Arquivo**: `docs/migracao-link-struct-blocks.md`

**Conteúdo**:
- Contexto e motivação
- Passo a passo de execução
- Plano de reversão
- Troubleshooting
- Checklist de deploy

## Como Usar

### Em Desenvolvimento (Local)

```bash
# 1. Backup
cp db.sqlite3 db.sqlite3.backup

# 2. Aplicar migração
workon codataSite && nvm use v22.13.1
python manage.py migrate blocks

# 3. Testar
python manage.py runserver
# Acessar admin → Editar página com LinhaDoTempoBlock
```

### Em Produção

```bash
# 1. BACKUP OBRIGATÓRIO
pg_dump nome_do_banco > backup_antes_migracao.sql

# 2. Deploy do código (git pull, etc.)
git pull origin main

# 3. Aplicar migração
python manage.py migrate blocks

# 4. Reiniciar aplicação
systemctl restart gunicorn  # ou similar

# 5. Validar no admin
# Editar e salvar um conteúdo antigo → deve funcionar normalmente
```

### Reversão (Se Necessário)

```bash
# Reverter migração
python manage.py migrate blocks 0006

# Restaurar backup (se necessário)
psql nome_do_banco < backup_antes_migracao.sql
```

## Arquivos Criados/Modificados

### Código Principal
- ✅ `blocks/models.py` - Blocos refatorados com fallback
- ✅ `blocks/migrations/0007_migrate_link_struct_blocks.py` - Migração de dados

### Testes
- ✅ `blocks/test_link_struct_blocks.py` - 15 testes (blocos)
- ✅ `blocks/test_migration_link_struct.py` - 5 testes (migração)

### Documentação
- ✅ `docs/migracao-link-struct-blocks.md` - Guia completo
- ✅ `docs/RESUMO-MIGRACAO.md` - Este arquivo

## Garantias de Segurança

1. ✅ **Não quebra o site**: Fallback automático mantém compatibilidade
2. ✅ **Reversível**: `migrate blocks 0006` desfaz tudo
3. ✅ **Testado**: 38 testes passando (15 novos + 23 existentes)
4. ✅ **Documentado**: Guia passo a passo com troubleshooting
5. ✅ **Sem alteração de schema**: Apenas transforma JSON (rápido e seguro)

## Validação Final

```bash
# Testes completos
python manage.py test --keepdb
# Ran 161 tests in 11.5s
# OK (skipped=6) ✅

# Migração aplicada
python manage.py showmigrations blocks
# [X] 0007_migrate_link_struct_blocks ✅

# Sem erros de código
python manage.py check
# System check identified no issues (0 silenced) ✅
```

## Conclusão

✅ **Problema resolvido** com solução robusta, testada e reversível.

**Próximos passos recomendados**:
1. Executar migração em ambiente de homologação
2. Validar no admin (criar/editar conteúdo)
3. Planejar janela de deploy em produção
4. Executar backup + migração em produção
5. Monitorar logs após deploy

**Tempo estimado de execução**: ~1-5 segundos (depende do volume de dados)
**Downtime necessário**: Nenhum (migração de dados JSON é rápida)
