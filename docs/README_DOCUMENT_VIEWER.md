# Sistema de Visualização de Documentos (Core)

Este sistema foi centralizado no app `core` para ser reutilizável em qualquer parte do projeto.

## Componentes

### 1. Views (core/views.py)

#### `DocumentServeView` (Classe)
View principal para servir documentos com visualização inline no navegador.

**Características:**
- Serve documentos com `Content-Disposition: inline`
- Configurações otimizadas para diferentes tipos de arquivo (PDF, imagens, Office)
- Headers de segurança (X-Frame-Options, CSP, etc.)
- Cache configurado por tipo de arquivo
- Logging detalhado para debugging

**URL:** `/core/documents/view/<document_id>/<filename>`

#### `document_serve_inline` (Função)
Versão simplificada da view acima para casos básicos.

### 2. Template Modal (core/templates/include/document_viewer_modal.html)

Modal Bootstrap reutilizável com:
- Visualizador de PDFs com iframe
- Suporte a imagens
- Fallback para outros tipos de arquivo
- Funções JavaScript globais: `showDocument()`, `tryPdfViewer()`, `tryAlternativeViewer()`

### 3. URLs (core/urls.py)

Namespace: `core`
- `core:document_serve_inline` - View principal de visualização

## Como Usar em Outros Apps

### 1. No Template HTML

```django
{% extends "base.html" %}

{% block content %}
<!-- Seu conteúdo aqui -->

<div class="acoes-documento">
  <!-- Botão para visualizar no modal -->
  <button class="icone-acao" 
          onclick="showDocument('{% url 'core:document_serve_inline' documento.id documento.filename %}', '{{ documento.title|escapejs }}')">
    <i class="bi bi-eye"></i>
  </button>
  
  <!-- Link direto (abre em nova aba) -->
  <a href="{% url 'core:document_serve_inline' documento.id documento.filename %}" 
     target="_blank" class="icone-acao">
    <i class="bi bi-eye"></i>
  </a>
  
  <!-- Download direto -->
  <a href="{{ documento.url }}" class="icone-acao">
    <i class="bi bi-download"></i>
  </a>
</div>

<!-- Incluir o modal no final do template -->
{% include "include/document_viewer_modal.html" %}
{% endblock %}
```

### 2. Função JavaScript

```javascript
// A função showDocument() já está disponível após incluir o modal
showDocument(url, titulo);

// Parâmetros:
// - url: URL completa do documento (use {% url 'core:document_serve_inline' ... %})
// - titulo: Título que aparecerá no modal
```

### 3. Exemplo Completo (Lista de Documentos)

```django
{% for doc in documentos %}
<div class="documento-item">
  <a href="{% url 'core:document_serve_inline' doc.arquivo.id doc.arquivo.filename %}" 
     target="_blank">
    {{ doc.title }}
  </a>
  
  <div class="acoes-documento">
    <button class="icone-acao" 
            onclick="showDocument('{% url 'core:document_serve_inline' doc.arquivo.id doc.arquivo.filename %}', '{{ doc.title|escapejs }}')">
      <i class="bi bi-eye"></i>
    </button>
    
    <a href="{{ doc.arquivo.url }}" class="icone-acao">
      <i class="bi bi-download"></i>
    </a>
  </div>
</div>
{% endfor %}

{% include "include/document_viewer_modal.html" %}
```

## SCSS Disponível

Classes personalizadas para estilizar os ícones de ação (já disponíveis no projeto):

```scss
.acoes-documento {
  display: flex;
  gap: 2rem; // 2.5rem no mobile
}

.icone-acao {
  background: none;
  border: none;
  cursor: pointer;
  
  i {
    font-size: 1.5rem; // 1.75rem no mobile
    transition: color 0.2s;
  }
  
  &:first-child i {
    color: $color-primary; // Azul
  }
  
  &:last-child i {
    color: $color-grey-600; // Cinza
  }
  
  &:hover i {
    opacity: 0.7;
  }
}
```

## Tipos de Arquivo Suportados

### PDFs
- Visualização inline via iframe/embed
- Headers otimizados para segurança
- Cache: 1 hora

### Imagens (jpg, png, gif, webp)
- Exibição direta no modal
- Cache: 24 horas

### Documentos Office (doc, docx, xls, xlsx)
- Forçado download (não suportam visualização inline)
- Cache desabilitado

### Outros
- Mensagem com link para abrir/baixar
- Cache: 30 minutos

## Configurações de Segurança

As views incluem automaticamente:
- `X-Frame-Options: SAMEORIGIN` (permite iframes no mesmo domínio)
- `Content-Security-Policy: frame-ancestors 'self'` (para PDFs)
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`
- CORS habilitado em desenvolvimento

## Logging

O sistema loga automaticamente:
- Requisições de documentos
- Erros ao servir arquivos
- Incompatibilidades de filename

Verifique os logs Django em caso de problemas.

## Exemplo de Uso: App "Editais"

```django
<!-- editais/templates/editais/editais_index_page.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
  <h1>Editais</h1>
  
  {% for edital in editais %}
  <div class="edital-item">
    <h3>{{ edital.title }}</h3>
    <p>{{ edital.description }}</p>
    
    {% if edital.arquivo_pdf %}
    <div class="acoes-documento">
      <button class="icone-acao" 
              onclick="showDocument('{% url 'core:document_serve_inline' edital.arquivo_pdf.id edital.arquivo_pdf.filename %}', '{{ edital.title|escapejs }}')">
        <i class="bi bi-eye"></i>
      </button>
      
      <a href="{{ edital.arquivo_pdf.url }}" class="icone-acao">
        <i class="bi bi-download"></i>
      </a>
    </div>
    {% endif %}
  </div>
  {% endfor %}
</div>

{% include "include/document_viewer_modal.html" %}
{% endblock %}
```

## Troubleshooting

### PDF não carrega no iframe
1. Verifique se a URL está acessível (abra em nova aba)
2. Confira os logs do Django para erros
3. O modal oferece automaticamente um visualizador alternativo

### Modal não abre
1. Verifique se Bootstrap JavaScript está carregado
2. Confirme que o include do modal está no template
3. Verifique o console do navegador para erros JS

### Arquivo não encontrado
1. Confirme que o documento existe no Wagtail
2. Verifique se o `document_id` e `filename` estão corretos
3. Confira os logs Django para detalhes do erro
