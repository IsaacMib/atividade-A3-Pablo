"""
Comando para criar configuração inicial do sistema.
Uso: python manage.py setup_inicial
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import ConfiguracaoSistema

User = get_user_model()


class Command(BaseCommand):
    help = 'Configura dados iniciais do sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando setup inicial...'))
        
        # Criar configuração do sistema
        if not ConfiguracaoSistema.objects.exists():
            config = ConfiguracaoSistema.objects.create(
                nome_sistema="Gestão de Estoque",
                descricao="Sistema completo de gestão de estoque",
                email_contato="contato@gestaoestoque.com",
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Configuração do sistema criada: {config.nome_sistema}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Configuração do sistema já existe')
            )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Setup inicial concluído com sucesso!'))
