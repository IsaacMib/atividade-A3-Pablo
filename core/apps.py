from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Este método é executado quando o Django está pronto.
        # É o local ideal para registrar configurações condicionalmente.
        from wagtail.contrib.settings.registry import register_setting
        from .models import ApiSettings

        if not settings.PORTAL_PROVEDOR_CONTEUDO:
            register_setting(ApiSettings, icon="link")
