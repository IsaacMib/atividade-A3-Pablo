"""
Utilitários para testes do projeto.

Este módulo contém funções auxiliares utilizadas nos testes de diferentes apps.
"""

from django.conf import settings
from wagtail.coreutils import get_supported_content_language_variant
from wagtail.models import Page, Locale


def ensure_root_page(locale_code: str | None = None):
    """
    Garante que existe uma página raiz configurada corretamente.
    
    Esta função é útil para testes que precisam de uma página raiz válida.
    Ela normaliza o código do locale, cria ou obtém o Locale correspondente,
    e garante que a página raiz tenha os campos necessários configurados.
    
    Args:
        locale_code: Código do locale (ex: 'pt-br', 'en'). 
                    Se None, usa settings.LANGUAGE_CODE.
    
    Returns:
        Page: A página raiz configurada.
    """
    if locale_code is None:
        locale_code = settings.LANGUAGE_CODE

    try:
        normalized_code = get_supported_content_language_variant(locale_code)
    except LookupError:
        normalized_code = locale_code

    locale, _ = Locale.objects.get_or_create(language_code=normalized_code)

    root = Page.get_first_root_node()
    if not root:
        root = Page.add_root(title="Root", slug="root")

    root.refresh_from_db()

    fields_to_update: list[str] = []

    if root.numchild is None:
        root.numchild = 0
        fields_to_update.append("numchild")

    if root.locale_id != locale.id:
        root.locale = locale
        fields_to_update.append("locale")

    if fields_to_update:
        root.save(update_fields=fields_to_update)

    return root
