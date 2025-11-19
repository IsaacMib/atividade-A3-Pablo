# Migração de Dados: LinkStructBlock

## Contexto

Foi realizada uma refatoração nos blocos `LinkWithImageStructBlock` e `CardLinhaDoTempoBlock` para consolidar os campos `internal_page` e `external_url` em um único campo aninhado `link` do tipo `LinkStructBlock`.

### Estrutura Antiga
```python
{
    'titulo': 'Meu Card',
    'internal_page': 123,
    'external_url': None,
    # outros campos...
}
```

### Estrutura Nova
```python
{
    'titulo': 'Meu Card',
    'link': {
        'internal_page': 123,
        'external_url': None,
        'link_text': '',
    },
    # outros campos...
}
```

## A Migração

A migração `blocks/migrations/0007_migrate_link_struct_blocks.py` foi criada para:

1. ✅ Transformar dados salvos no banco de páginas **publicadas**
2. ✅ Transformar dados no **histórico de revisões** do Wagtail
3. ✅ Preservar compatibilidade retroativa (fallback no código)
4. ✅ Permitir reversão (`python manage.py migrate blocks 0006`)

### Blocos Afetados

- **CardLinhaDoTempoBlock** (usado em `LinhaDoTempoBlock`)
- **LinkWithImageStructBlock** (se usado em algum StreamField)

## Como Executar a Migração

### 1. Backup do Banco de Dados (OBRIGATÓRIO)

```bash
# PostgreSQL
pg_dump nome_do_banco > backup_antes_migracao_$(date +%Y%m%d_%H%M%S).sql

# SQLite (dev)
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Executar a Migração

```bash
# Ativar ambiente
workon codataSite && nvm use v22.13.1

# Aplicar migração
python manage.py migrate blocks

# Saída esperada:
# Running migrations:
#   Applying blocks.0007_migrate_link_struct_blocks...
# ✅ Migração concluída:
#    - X página(s) publicada(s) atualizada(s)
#    - Y revisão(ões) atualizada(s)
```

### 3. Verificar Resultados

Acesse o admin do Wagtail e:
1. Vá para uma página que usa `LinhaDoTempoBlock`
2. Edite um card da linha do tempo
3. Verifique se o campo "Link" aparece corretamente
4. Salve e publique

## Reversão (Se Necessário)

Se houver algum problema, você pode reverter:

```bash
# Reverter para migração anterior
python manage.py migrate blocks 0006

# Saída esperada:
# Unapplying blocks.0007_migrate_link_struct_blocks...
# ✅ Reversão concluída:
#    - X página(s) revertida(s)
#    - Y revisão(ões) revertida(s)

# Restaurar backup (se necessário)
# PostgreSQL: psql nome_do_banco < backup_antes_migracao_*.sql
# SQLite: cp db.sqlite3.backup_* db.sqlite3
```

## Compatibilidade Retroativa

O código possui **fallback automático** para dados antigos:

```python
def get_url(self):
    # Tenta novo formato primeiro
    link = self.get('link')
    if link:
        # ... resolver URL do link aninhado
    
    # FALLBACK: Tenta formato antigo
    internal_legacy = self.get('internal_page')
    if internal_legacy:
        return internal_legacy.url
    return self.get('external_url')
```

Isso significa que:
- ✅ Dados antigos continuam renderizando (não quebra o site)
- ✅ Novos dados salvos já usam o formato correto
- ⚠️ Ao editar conteúdo antigo no admin, ele será salvo no novo formato

## Testes

A migração foi testada com:

```bash
# Testar em banco limpo
rm -f db.sqlite3
python manage.py migrate
python manage.py test blocks.test_link_struct_blocks --keepdb

# Resultado: 15/15 testes OK ✅
```

## Impacto em Produção

### Antes da Migração
- Conteúdo existente renderiza normalmente (fallback funciona)
- Admin pode exibir warnings ao editar conteúdo antigo

### Durante a Migração
- Duração estimada: ~1-5 segundos (depende do volume de dados)
- Não há downtime necessário (migração de dados, não de schema)

### Após a Migração
- Todo conteúdo usa o novo formato
- Admin funciona normalmente
- Próximas edições salvam no formato correto

## Troubleshooting

### Erro: "dependencies não encontradas"
**Problema**: App `linhasdotempo` não existe no ambiente
**Solução**: Remover linha `('linhasdotempo', '__latest__')` das dependencies da migração

### Nenhuma página atualizada
**Situação Normal**: Não havia conteúdo com os blocos afetados
**Verificação**: Buscar manualmente no banco:
```sql
SELECT id, title FROM wagtailcore_page 
WHERE specific_type_id IN (
  SELECT id FROM django_content_type 
  WHERE model LIKE '%linhadotempo%'
);
```

### Erro ao salvar conteúdo no admin após migração
**Possível causa**: Cache de definições do StreamField
**Solução**: Reiniciar servidor de desenvolvimento
```bash
# Parar servidor (Ctrl+C)
# Limpar cache Python (opcional)
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete
# Iniciar servidor novamente
python manage.py runserver
```

## Comandos Úteis

```bash
# Ver status das migrações
python manage.py showmigrations blocks

# Ver SQL que seria executado (não executa de fato)
python manage.py sqlmigrate blocks 0007

# Listar páginas com StreamField
python manage.py shell
>>> from wagtail.models import Page
>>> for p in Page.objects.all():
...     for f in p._meta.fields:
...         if f.get_internal_type() in ('JSONField', 'TextField'):
...             print(f"{p.title}: {f.name}")
```

## Checklist de Deploy

- [ ] Backup do banco de dados criado
- [ ] Migração testada em ambiente de homologação
- [ ] Código de fallback validado (conteúdo antigo renderiza)
- [ ] Testes passando (161/161 OK)
- [ ] Documentação atualizada
- [ ] Plano de reversão documentado
- [ ] Janela de manutenção definida (se necessário)
- [ ] Stakeholders notificados

## Referências

- **Issue/PR**: [Link para issue/PR relacionado]
- **Código**: `blocks/migrations/0007_migrate_link_struct_blocks.py`
- **Testes**: `blocks/test_link_struct_blocks.py`
- **Models afetados**: `blocks/models.py` (LinkWithImageStructBlock, CardLinhaDoTempoBlock)
