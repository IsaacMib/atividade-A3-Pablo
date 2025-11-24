"""
Comando para exibir informações do sistema.
Uso: python manage.py info_sistema
"""

import sys
import django
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

from core.models import ConfiguracaoSistema, Log


class Command(BaseCommand):
    help = 'Exibe informações sobre o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(self.style.SUCCESS('  INFORMAÇÕES DO SISTEMA'))
        self.stdout.write(self.style.SUCCESS('═' * 60))
        
        # Python e Django
        self.stdout.write('\n📦 Versões:')
        self.stdout.write(f'  Python: {sys.version.split()[0]}')
        self.stdout.write(f'  Django: {django.get_version()}')
        
        # Banco de dados
        self.stdout.write('\n🗄️  Banco de Dados:')
        db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]
        self.stdout.write(f'  Engine: {db_engine}')
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migrations = cursor.fetchone()[0]
        self.stdout.write(f'  Migrações aplicadas: {migrations}')
        
        # Configuração do sistema
        try:
            config = ConfiguracaoSistema.get_config()
            self.stdout.write('\n⚙️  Configuração:')
            self.stdout.write(f'  Nome: {config.nome_sistema}')
            self.stdout.write(f'  Email: {config.email_contato or "Não configurado"}')
            self.stdout.write(f'  Manutenção: {"Ativo" if config.manutencao_ativa else "Inativo"}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Configuração não encontrada: {e}'))
        
        # Estatísticas
        self.stdout.write('\n📊 Estatísticas:')
        total_logs = Log.objects.count()
        self.stdout.write(f'  Total de logs: {total_logs}')
        
        # Ambiente
        self.stdout.write('\n🌍 Ambiente:')
        self.stdout.write(f'  DEBUG: {settings.DEBUG}')
        self.stdout.write(f'  AMBIENTE: {settings.AMBIENTE}')
        self.stdout.write(f'  VERSÃO: {settings.SISTEMA_VERSAO}')
        
        self.stdout.write('\n' + '═' * 60)
