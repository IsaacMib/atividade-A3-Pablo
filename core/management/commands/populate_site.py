"""
Comando Django para popular o site com dados de demonstração.

Uso: python manage.py populate_site
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from wagtail.models import Site, Locale
from wagtail.images.models import Image
from wagtail.documents.models import Document
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import random
from datetime import timedelta

from home.models import HomePage
from noticias.models import NoticiasIndexPages, NoticiasPage, CategoriaNoticias
from wagtail.models import Page


class Command(BaseCommand):
    help = 'Popula o site com dados de demonstração'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🌱 Iniciando população do site...'))
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Limpando dados existentes...'))
            self.clear_data()
        
        # Criar usuários
        self.stdout.write('👤 Criando usuários...')
        self.create_users()
        
        # Criar categorias de notícias
        self.stdout.write('📂 Criando categorias...')
        self.create_categories()
        
        # Criar imagens de demonstração
        self.stdout.write('🖼️  Criando imagens de demonstração...')
        self.create_demo_images()
        
        # Criar estrutura de páginas
        self.stdout.write('📄 Criando estrutura de páginas...')
        self.create_page_structure()
        
        # Criar notícias
        self.stdout.write('📰 Criando notícias...')
        self.create_noticias()
        
        self.stdout.write(self.style.SUCCESS('✅ Site populado com sucesso!'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Credenciais de acesso:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Editor: editor / editor123')

    def clear_data(self):
        """Limpa dados existentes (exceto root page)."""
        # Não limpar usuários superuser, apenas os criados pelo script
        User.objects.filter(username__in=['admin', 'editor']).delete()
        
        # Limpar categorias
        CategoriaNoticias.objects.all().delete()
        
        # Limpar imagens de demonstração
        Image.objects.filter(title__startswith='Demo').delete()

    def create_users(self):
        """Cria usuários de teste."""
        # Grupo de editores
        editores_group, _ = Group.objects.get_or_create(name='Editores')
        
        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@neuroprev.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(f'  ✓ Criado: admin (superuser)')
        
        # Editor
        if not User.objects.filter(username='editor').exists():
            editor = User.objects.create_user(
                username='editor',
                email='editor@neuroprev.com',
                password='editor123',
                first_name='Editor',
                last_name='Conteúdo',
                is_staff=True
            )
            editor.groups.add(editores_group)
            self.stdout.write(f'  ✓ Criado: editor (staff)')

    def create_categories(self):
        """Cria categorias de notícias."""
        categorias = [
            ('Pesquisa', 'Estudos e descobertas científicas sobre autismo'),
            ('Diagnóstico', 'Avanços e métodos de diagnóstico precoce'),
            ('Tecnologia', 'Ferramentas e sistemas de apoio'),
            ('Educação', 'Informações e recursos educacionais'),
            ('Comunidade', 'Eventos e ações comunitárias'),
        ]
        
        for nome, descricao in categorias:
            categoria, created = CategoriaNoticias.objects.get_or_create(
                nome=nome,
                defaults={'descricao': descricao}
            )
            if created:
                self.stdout.write(f'  ✓ Categoria: {nome}')

    def create_demo_images(self):
        """Cria imagens de demonstração."""
        colors = [
            ((52, 152, 219), 'blue'),    # Azul
            ((46, 204, 113), 'green'),   # Verde
            ((155, 89, 182), 'purple'),  # Roxo
            ((241, 196, 15), 'yellow'),  # Amarelo
            ((231, 76, 60), 'red'),      # Vermelho
        ]
        
        self.demo_images = []
        
        for i, (color, name) in enumerate(colors, 1):
            # Criar imagem PIL
            img = PILImage.new('RGB', (800, 600), color=color)
            
            # Salvar em BytesIO
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            # Criar SimpleUploadedFile
            img_file = SimpleUploadedFile(
                f'demo_{name}.jpg',
                img_io.read(),
                content_type='image/jpeg'
            )
            
            # Criar objeto Image
            image = Image.objects.create(
                title=f'Demo Image {i} ({name})',
                file=img_file,
            )
            self.demo_images.append(image)
            self.stdout.write(f'  ✓ Imagem: demo_{name}.jpg')

    def create_page_structure(self):
        """Cria estrutura básica de páginas."""
        # Obter root page e site
        locale = Locale.get_default()
        site = Site.objects.filter(is_default_site=True).first()
        
        if not site:
            self.stdout.write(self.style.ERROR('  ✗ Nenhum site padrão encontrado!'))
            return
        
        root_page = site.root_page
        
        # Verificar se HomePage já existe
        home_page = HomePage.objects.first()
        if not home_page:
            # Criar HomePage
            home_page = HomePage(
                title='NeuroPrev - Triagem Precoce de Autismo',
                slug='home',
                locale=locale,
            )
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            self.stdout.write('  ✓ Página: Home')
            
            # Atualizar site root
            site.root_page = home_page
            site.save()
        
        # Criar NoticiasIndexPages se não existir
        noticias_index = NoticiasIndexPages.objects.first()
        if not noticias_index:
            noticias_index = NoticiasIndexPages(
                title='Notícias',
                slug='noticias',
                locale=locale,
                descricao='Últimas notícias e atualizações sobre autismo e diagnóstico precoce',
            )
            home_page.add_child(instance=noticias_index)
            noticias_index.save_revision().publish()
            self.stdout.write('  ✓ Página: Notícias (Index)')
        
        self.home_page = home_page
        self.noticias_index = noticias_index

    def create_noticias(self):
        """Cria notícias de demonstração."""
        categorias = list(CategoriaNoticias.objects.all())
        
        if not categorias:
            self.stdout.write(self.style.WARNING('  ! Nenhuma categoria encontrada, pulando notícias'))
            return
        
        noticias_data = [
            {
                'title': 'Sistema NeuroPrev alcança 95% de precisão em testes',
                'intro': 'Novo sistema de IA demonstra alta eficácia na detecção precoce de sinais de autismo.',
                'categoria': 'Tecnologia',
            },
            {
                'title': 'Importância do diagnóstico precoce no autismo',
                'intro': 'Estudos mostram que intervenção antes dos 3 anos pode melhorar significativamente o desenvolvimento.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Como funciona a análise multimodal de comportamento',
                'intro': 'Entenda como o sistema combina vídeo, áudio e questionários para avaliação completa.',
                'categoria': 'Tecnologia',
            },
            {
                'title': 'Webinar gratuito sobre sinais precoces de autismo',
                'intro': 'Participe do evento online com especialistas em desenvolvimento infantil.',
                'categoria': 'Comunidade',
            },
            {
                'title': 'Nova pesquisa revela padrões de comunicação em crianças autistas',
                'intro': 'Estudo identifica marcadores linguísticos que podem auxiliar no diagnóstico.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Guia para pais: O que observar no desenvolvimento',
                'intro': 'Orientações sobre marcos de desenvolvimento e quando buscar avaliação.',
                'categoria': 'Educação',
            },
            {
                'title': 'IA ajuda profissionais de saúde a identificar TEA',
                'intro': 'Ferramenta auxilia pediatras e psicólogos na triagem inicial de autismo.',
                'categoria': 'Diagnóstico',
            },
            {
                'title': 'Resultados positivos em testes piloto do NeuroPrev',
                'intro': 'Sistema foi testado com 500 famílias apresentando resultados promissores.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Acessibilidade no diagnóstico: democratizando o acesso',
                'intro': 'Como a tecnologia pode levar triagem precoce para áreas remotas.',
                'categoria': 'Comunidade',
            },
            {
                'title': 'Privacidade e segurança no processamento de dados',
                'intro': 'Conheça as medidas de proteção de dados sensíveis no sistema NeuroPrev.',
                'categoria': 'Tecnologia',
            },
        ]
        
        for i, data in enumerate(noticias_data):
            # Buscar categoria
            categoria = CategoriaNoticias.objects.filter(nome=data['categoria']).first()
            if not categoria:
                categoria = random.choice(categorias)
            
            # Criar notícia
            noticia = NoticiasPage(
                title=data['title'],
                slug=f'noticia-{i+1}',
                locale=Locale.get_default(),
                descricao=data['intro'],
                intro=data['intro'],
                categoria=categoria,
                data=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
            
            # Adicionar imagem de destaque aleatória
            if self.demo_images:
                noticia.imagem_destaque = random.choice(self.demo_images)
            
            # Adicionar ao índice de notícias
            self.noticias_index.add_child(instance=noticia)
            noticia.save_revision().publish()
            
            self.stdout.write(f'  ✓ Notícia: {data["title"][:50]}...')
