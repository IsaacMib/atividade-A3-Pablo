from django import template

register = template.Library()

@register.filter
def result_type(result):
    # Para objetos Page do Wagtail
    if hasattr(result, "content_type") and hasattr(result.content_type, "model"):
        tipo = result.content_type.model
        if tipo.lower() == "noticiaspage":
            return "Notícia"
        if tipo.lower() == "document":
            return "Arquivo"
        if tipo.lower() == "image":
            return "Imagem"
        return tipo.replace('_', ' ').title()
    # Para arquivos e imagens importados
    elif result.__class__.__name__ == "PloneImportedFile":
        return "Arquivo"
    elif result.__class__.__name__ == "PloneImportedImage":
        return "Imagem"
    # Caso seja string ou outro tipo
    elif isinstance(result, str):
        return result.replace('_', ' ').title()
    return ""