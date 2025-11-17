"""
Comando para limpar logs antigos.
Uso: python manage.py limpar_logs --dias 30
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import Log


class Command(BaseCommand):
    help = 'Remove logs mais antigos que X dias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de dias para manter os logs (padrão: 30)',
        )

    def handle(self, *args, **kwargs):
        dias = kwargs['dias']
        data_limite = timezone.now() - timedelta(days=dias)
        
        self.stdout.write(f'Removendo logs anteriores a {data_limite.strftime("%d/%m/%Y")}...')
        
        logs_deletados = Log.objects.filter(criado_em__lt=data_limite).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {logs_deletados[0]} logs removidos com sucesso!'
            )
        )
