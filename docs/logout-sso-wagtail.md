# Logout com SSO para Wagtail Admin

## Descrição

Esta implementação garante que quando um usuário faz logout pelo admin do Wagtail (manager), ele também seja desconectado do sistema SSO (Single Sign-On), evitando que permaneça logado no Keycloak após sair do sistema.

## Como funciona

### 1. Configuração condicional de URLs

No arquivo `neuroathena/urls.py`, quando `HABILITAR_SSO_LOGIN=True`:

- **URL padrão do Wagtail**: `/admin/manager/logout/` → redireciona para nossa view customizada `wagtail_logout_with_sso`
- **URL do allauth**: `/admin/logout/` → continua usando o `KeycloakAdapter` existente

### 2. View customizada de logout

A view `wagtail_logout_with_sso` em `neuroathena/views.py`:

1. **Verifica se o SSO está habilitado** e se o usuário tem provedor SSO configurado
2. **Faz logout do SSO** usando a mesma lógica do `KeycloakAdapter`
3. **Faz logout local** do Django
4. **Redireciona** para a página de login (`/admin/login/`)

### 3. Reutilização da lógica existente

A implementação reutiliza as funções do `KeycloakAdapter`:
- `obter_provedor_recente()` - para obter o provedor SSO do usuário
- Mesma lógica de logout do SSO com tokens de acesso e refresh
- Mesmo tratamento de erros e logging

## Cenários de uso

### 1. Usuário logado via SSO no Wagtail admin
- **Ação**: Clica em "Logout" no admin do Wagtail
- **Resultado**: Desconectado do Wagtail E do SSO (Keycloak)

### 2. Usuário logado via SSO no sistema geral
- **Ação**: Faz logout através do allauth (`/admin/logout/`)
- **Resultado**: Continua usando o `KeycloakAdapter` original

### 3. Usuário local (sem SSO)
- **Ação**: Faz logout
- **Resultado**: Apenas logout local do Django

### 4. SSO desabilitado (`HABILITAR_SSO_LOGIN=False`)
- **Comportamento**: URLs padrão do Wagtail sem modificações

## Arquivos modificados

1. **`neuroathena/views.py`**
   - Adicionada view `wagtail_logout_with_sso`
   - Funções auxiliares para logout do SSO

2. **`neuroathena/urls.py`**
   - Sobrescrita da URL `wagtailadmin_logout` quando SSO habilitado

3. **`neuroathena/tests.py`**
   - Testes para verificar funcionamento da implementação

## Configuração

### Variáveis de ambiente necessárias

```bash
HABILITAR_SSO_LOGIN=True
KEYCLOAK_SERVER_URL_LOGOUT=https://seu-keycloak.com/auth/realms/seu-realm/protocol/openid-connect/logout
```

### Dependências

- `allauth` configurado com Keycloak
- Módulo `auth_keycloak` com o `KeycloakAdapter`

## Logs

A implementação registra logs para troubleshooting:

- **INFO**: Tentativas de logout do SSO
- **ERROR**: Falhas na obtenção de tokens ou na requisição de logout
- **WARNING**: Usuários com múltiplos provedores

## Compatibilidade

- ✅ Funciona com SSO habilitado e desabilitado
- ✅ Não interfere no funcionamento do allauth
- ✅ Mantém compatibilidade com logout local
- ✅ Reutiliza lógica existente do `KeycloakAdapter`

## Teste da funcionalidade

Para testar se está funcionando:

1. **Configure SSO**: `HABILITAR_SSO_LOGIN=True`
2. **Faça login via SSO** no admin do Wagtail
3. **Clique em logout** no admin
4. **Verifique** se foi desconectado tanto do Wagtail quanto do Keycloak

### Teste automatizado

```bash
python manage.py test neuroathena.tests -v 2
```

## Troubleshooting

### Problema: Usuário não é desconectado do SSO

**Possíveis causas**:
- `KEYCLOAK_SERVER_URL_LOGOUT` não configurado
- Tokens de acesso/refresh expirados ou inválidos
- Problemas de conectividade com o Keycloak

**Solução**: Verificar logs do Django para detalhes do erro

### Problema: URLs não funcionam

**Possíveis causas**:
- `HABILITAR_SSO_LOGIN` não está `True`
- Cache de URLs não foi limpo

**Solução**: Reiniciar o servidor Django
