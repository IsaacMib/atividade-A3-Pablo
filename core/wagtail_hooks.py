from django.urls import reverse
from django.conf import settings
from wagtail import hooks


@hooks.register('construct_settings_menu')
def hide_api_settings_menu_item(request, menu_items):

    if not settings.API_CONTEUDO_AGRUPADO:
        menu_items[:] = [
            item for item in menu_items
            if item.name != 'apisettings'
        ]