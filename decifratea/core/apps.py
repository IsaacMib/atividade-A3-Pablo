"""
Configuração do app Core.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        """
        Código executado quando o app é carregado.
        Coloque aqui imports de signals, registros, etc.
        """
        # Importar signals se houver
        # import core.signals
        pass
