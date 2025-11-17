# Templatetag: aviso_administrador

## Descrição
Templatetag reutilizável que exibe avisos/alertas visíveis **apenas para usuários autenticados**.

## Localização
- **Arquivo**: `core/templatetags/page_utils.py`
- **Template**: `core/templates/tags/aviso_administrador.html`

## Uso

### 1. Carregar a templatetag no template
```django
{% load page_utils %}
```

### 2. Uso básico (mensagem e tipo padrão)
```django
{% aviso_administrador %}
```
Exibe: Alert azul (info) com mensagem padrão.

### 3. Uso com mensagem customizada
```django
{% aviso_administrador mensagem="Você está visualizando esse conteúdo porque tem permissão de editar." %}
```

### 4. Uso com tipo de alert customizado
```django
{% aviso_administrador mensagem="Esta página redireciona usuários não autenticados." tipo="warning" %}
```

### 5. Uso completo
```django
{% aviso_administrador mensagem="Atenção: Esta ação é irreversível!" tipo="danger" %}
```

## Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `mensagem` | string | "Esta página está sendo exibida porque você está autenticado no sistema." | Mensagem a ser exibida |
| `tipo` | string | "info" | Tipo do alert Bootstrap |

### Tipos de alert disponíveis:
- `info` - Alert azul (informação)
- `warning` - Alert amarelo (aviso)
- `danger` - Alert vermelho (perigo)
- `success` - Alert verde (sucesso)

## Comportamento

1. **Usuário NÃO autenticado**: Nada é exibido
2. **Usuário autenticado**: Exibe o alert com:
   - Ícone de informação
   - Título "Informação para Administradores:"
   - Mensagem configurável
   - Botão de fechar (dismiss)

## Exemplos de uso no projeto

### RedirectPage (`paginas/templates/paginas/redirect_page.html`)
```django
{% load wagtailcore_tags page_utils %}

<h2 class="redirect-page--title">{{ page.title }}</h2>

{% aviso_administrador mensagem="Esta página está sendo exibida porque você está autenticado no sistema. Usuários não autenticados serão redirecionados automaticamente para o destino." tipo="warning" %}
```

### AgendaDoDiaPage (`agenda/templates/agenda/agenda_do_dia_page.html`)
```django
{% load wagtailcore_tags wagtailimages_tags page_utils %}

<h1 class="agenda-do-dia--title">{{ page.title }}</h1>

{% aviso_administrador mensagem="Você está visualizando esse conteúdo porque tem permissão de editar." tipo="info" %}
```

## Estilo CSS

O alert usa classes Bootstrap padrão:
- `.alert`
- `.alert-{tipo}` (info, warning, danger, success)
- `.alert-dismissible`

Para tema escuro, as cores são ajustadas automaticamente pelo SCSS do projeto em `redirect_page_cores_escuro.scss`:

```scss
[data-theme="dark"] {
  .alert-warning {
    background-color: rgba(variables.$color-warning, 0.15) !important;
    color: variables.$color-grey-100 !important;
    border-color: rgba(variables.$color-warning, 0.3) !important;
    
    strong {
      color: variables.$color-warning !important;
    }
  }
}
```

## Acessibilidade

- ✅ `role="alert"` para leitores de tela
- ✅ `aria-label="Fechar"` no botão de dismiss
- ✅ Ícone Bootstrap Icons (`bi-info-circle`)
- ✅ Contraste adequado (WCAG AA)
- ✅ Suporte a tema escuro

## Vantagens

1. **Reutilizável**: Único código, múltiplos templates
2. **Consistente**: Mesmo estilo em todo o site
3. **Flexível**: Mensagem e tipo configuráveis
4. **Semântico**: HTML correto com ARIA
5. **Responsivo**: Funciona em todos os dispositivos
6. **Acessível**: Segue padrões WCAG
7. **Temático**: Adapta-se ao tema claro/escuro

## Quando usar

- Páginas que só administradores devem ver
- Conteúdo que redireciona usuários não autenticados
- Informações sobre comportamento condicional
- Avisos de edição/permissões
- Mensagens de debug/desenvolvimento
