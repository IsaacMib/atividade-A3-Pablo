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
        
        # Popular blocos da HomePage
        self.populate_homepage_blocks()
        
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
        
        # Limpar notícias
        from noticias.models import NoticiasPage
        NoticiasPage.objects.all().delete()
        
        # Nota: Não deletar imagens para evitar problemas com tasks do Wagtail

    def create_users(self):
        """Cria usuários de teste."""
        # Grupo de editores
        editores_group, _ = Group.objects.get_or_create(name='Editores')
        
        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@neuroathena.com.br',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            self.stdout.write(f'  ✓ Criado: admin (superuser)')
        
        # Editor
        if not User.objects.filter(username='editor').exists():
            editor = User.objects.create_user(
                username='editor',
                email='editor@neuroathena.com.br',
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
            'Pesquisa',
            'Diagnóstico',
            'Tecnologia',
            'Educação',
            'Comunidade',
        ]
        
        for nome in categorias:
            categoria, created = CategoriaNoticias.objects.get_or_create(nome=nome)
            if created:
                self.stdout.write(f'  ✓ Categoria: {nome}')

    def create_demo_images(self):
        """Cria imagens de demonstração."""
        from wagtail.models import Collection
        
        # Garantir que existe Collection root
        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name="Root")
        
        colors = [
            ((52, 152, 219), 'blue'),    # Azul
            ((46, 204, 113), 'green'),   # Verde
            ((155, 89, 182), 'purple'),  # Roxo
            ((241, 196, 15), 'yellow'),  # Amarelo
            ((231, 76, 60), 'red'),      # Vermelho
        ]
        
        self.demo_images = []
        
        for i, (color, name) in enumerate(colors, 1):
            # Verificar se imagem já existe
            existing = Image.objects.filter(title=f'Demo Image {i} ({name})').first()
            if existing:
                self.demo_images.append(existing)
                continue
            
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
            try:
                image = Image.objects.create(
                    title=f'Demo Image {i} ({name})',
                    file=img_file,
                )
                self.demo_images.append(image)
                self.stdout.write(f'  ✓ Imagem: demo_{name}.jpg')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Erro ao criar imagem {name}: {e}'))
                continue

    def create_page_structure(self):
        """Cria estrutura básica de páginas."""
        # Obter root page e site
        locale = Locale.get_default()
        site = Site.objects.filter(is_default_site=True).first()
        
        if not site:
            self.stdout.write(self.style.ERROR('  ✗ Nenhum site principal encontrado!'))
            return
        
        root_page = site.root_page
        
        # Verificar se HomePage já existe
        home_page = HomePage.objects.first()
        if not home_page:
            # Se não existe, usar a root page como HomePage
            # Verificar se root já é HomePage
            if isinstance(root_page.specific, HomePage):
                home_page = root_page.specific
                self.stdout.write('  ✓ Página: Home (root existente)')
            else:
                # Criar nova HomePage como filha
                try:
                    home_page = HomePage(
                        title='NEUROATHENA - Triagem Precoce de Autismo',
                        slug='home',
                        locale=locale,
                    )
                    root_page.add_child(instance=home_page)
                    home_page.save_revision().publish()
                    self.stdout.write('  ✓ Página: Home (criada)')
                    
                    # Atualizar site root
                    site.root_page = home_page
                    site.save()
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ! Erro ao criar HomePage: {e}'))
                    self.stdout.write('  ! Usando root page como fallback')
                    home_page = None
        else:
            self.stdout.write('  ✓ Página: Home (já existe)')
        
        # Criar NoticiasIndexPages se não existir
        noticias_index = NoticiasIndexPages.objects.first()
        if not noticias_index and home_page:
            try:
                noticias_index = NoticiasIndexPages(
                    title='Notícias',
                    slug='noticias',
                    locale=locale,
                    descricao='Últimas notícias e atualizações sobre autismo e diagnóstico precoce',
                )
                home_page.add_child(instance=noticias_index)
                noticias_index.save_revision().publish()
                self.stdout.write('  ✓ Página: Notícias (Index criada)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Erro ao criar NoticiasIndexPages: {e}'))
        elif noticias_index:
            self.stdout.write('  ✓ Página: Notícias (já existe)')
        
        self.home_page = home_page
        self.noticias_index = noticias_index
    
    def populate_homepage_blocks(self):
        """Popula a HomePage com blocos Wagtail configurados."""
        self.stdout.write('🎨 Configurando blocos da HomePage...')
        
        # Criar conteúdo dos blocos
        homepage_content = [
            # 1. Hero Block
            ('hero', {
                'titulo': 'NEUROATHENA',
                'subtitulo': 'Triagem Precoce de Autismo com IA Multimodal',
                'descricao': 'Sistema inteligente que combina análise de vídeo, áudio e questionários para auxiliar na detecção precoce de sinais do Transtorno do Espectro Autista (TEA) em crianças.',
                'cta_primario_texto': 'Começar Triagem',
                'cta_primario_url': '/triagem/nova/',
                'cta_secundario_texto': 'Saiba Mais',
                'cta_secundario_url': '/sobre/',
            }),
            
            # 2. Features Grid
            ('features_grid', {
                'titulo_secao': 'Como Funciona a Athena',
                'funcionalidades': [
                    {
                        'icone': '🎥',
                        'titulo': 'Análise de Vídeo',
                        'descricao': 'Processamento de vídeos da criança para identificar padrões de comportamento e interação social.',
                    },
                    {
                        'icone': '🔊',
                        'titulo': 'Análise de Áudio',
                        'descricao': 'Avaliação de padrões de fala, prosódia e comunicação verbal da criança.',
                    },
                    {
                        'icone': '📝',
                        'titulo': 'Questionários',
                        'descricao': 'Formulários baseados em instrumentos validados como M-CHAT-R para complementar a análise.',
                    },
                    {
                        'icone': '🧠',
                        'titulo': 'IA Multimodal',
                        'descricao': 'Fusão inteligente de múltiplas fontes de dados para análise mais precisa e confiável.',
                    },
                    {
                        'icone': '📊',
                        'titulo': 'Painel Diário',
                        'descricao': 'Acompanhamento contínuo do desenvolvimento com registro de observações e marcos.',
                    },
                    {
                        'icone': '🔒',
                        'titulo': 'Privacidade LGPD',
                        'descricao': 'Total conformidade com LGPD, dados criptografados e controle total pelos responsáveis.',
                    },
                ]
            }),
            
            # 3. Título - Vantagens
            ('titulo', {
                'texto': 'Por Que Escolher o NEUROATHENA?',
                'tag': 'h2',
                'alinhamento': 'center',
            }),
            
            # 4. Grid de Imagens - Vantagens
            ('programa', {
                'titulo': 'Benefícios do Sistema',
                'descricao': '<p>O NEUROATHENA oferece uma abordagem moderna e acessível para triagem precoce de autismo com IA.</p>',
                'imagens': [
                    {
                        'imagem': self.demo_images[0].id if self.demo_images else None,
                        'titulo': 'Detecção Precoce',
                        'descricao': 'Identificação de sinais antes dos 3 anos de idade, período crítico para intervenção.',
                    },
                    {
                        'imagem': self.demo_images[1].id if self.demo_images else None,
                        'titulo': 'Acessível e Remoto',
                        'descricao': 'Faça a triagem de casa, sem necessidade de deslocamento ou longas esperas.',
                    },
                    {
                        'imagem': self.demo_images[2].id if self.demo_images else None,
                        'titulo': 'Baseado em Evidências',
                        'descricao': 'Algoritmos treinados com dados científicos e instrumentos validados internacionalmente.',
                    },
                    {
                        'imagem': self.demo_images[3].id if self.demo_images else None,
                        'titulo': 'Apoio aos Profissionais',
                        'descricao': 'Ferramenta auxiliar para pediatras e psicólogos na tomada de decisão clínica.',
                    },
                ] if self.demo_images else []
            }),
            
            # 5. Título - Processo
            ('titulo', {
                'texto': 'Processo de Triagem',
                'tag': 'h2',
                'alinhamento': 'center',
            }),
            
            # 6. Linha do Tempo - Etapas
            ('linha_do_tempo', {
                'titulo': 'Etapas da Triagem',
                'descricao': '<p>Siga estas etapas simples para realizar a triagem completa:</p>',
                'eventos': [
                    {
                        'titulo': '1. Cadastro',
                        'data': '2024-01-01',
                        'descricao': '<p>Crie uma conta e forneça informações básicas sobre a criança.</p>',
                    },
                    {
                        'titulo': '2. Upload de Vídeos',
                        'data': '2024-01-02',
                        'descricao': '<p>Envie vídeos curtos da criança em diferentes situações sociais.</p>',
                    },
                    {
                        'titulo': '3. Gravação de Áudio',
                        'data': '2024-01-03',
                        'descricao': '<p>Grave amostras de fala e comunicação da criança.</p>',
                    },
                    {
                        'titulo': '4. Questionários',
                        'data': '2024-01-04',
                        'descricao': '<p>Preencha questionários sobre comportamento e desenvolvimento.</p>',
                    },
                    {
                        'titulo': '5. Análise IA',
                        'data': '2024-01-05',
                        'descricao': '<p>Sistema processa os dados com algoritmos de IA multimodal.</p>',
                    },
                    {
                        'titulo': '6. Resultados',
                        'data': '2024-01-06',
                        'descricao': '<p>Receba relatório detalhado com recomendações e próximos passos.</p>',
                    },
                ]
            }),
            
            # 7. Título - Últimas Notícias
            ('titulo', {
                'texto': 'Últimas Notícias',
                'tag': 'h2',
                'alinhamento': 'center',
            }),
            
            # 8. Lista de Notícias
            ('noticias', {
                'titulo': 'Fique por dentro das novidades',
                'quantidade': 6,
                'exibir_data': True,
                'exibir_categoria': True,
            }),
            
            # 9. CTA Final
            ('cta', {
                'titulo': 'Pronto para Começar?',
                'descricao': '<p>Inicie a triagem agora mesmo e dê o primeiro passo para o desenvolvimento saudável da sua criança.</p>',
                'botao_texto': 'Começar Triagem Gratuita',
                'botao_url': '/triagem/nova/',
                'imagem_fundo': self.demo_images[4].id if self.demo_images else None,
            }),
            
            # 10. Acordeon - FAQ
            ('secao_informativa', {
                'titulo': 'Perguntas Frequentes',
                'itens': [
                    {
                        'titulo': 'O NEUROATHENA substitui o diagnóstico profissional?',
                        'conteudo': '<p>Não. O NEUROATHENA é uma ferramenta de <strong>triagem</strong>, não de diagnóstico. Ele auxilia na identificação de sinais que podem indicar a necessidade de uma avaliação mais aprofundada por profissionais especializados.</p>',
                    },
                    {
                        'titulo': 'Qual a idade recomendada para usar o sistema?',
                        'conteudo': '<p>O sistema é projetado para crianças entre <strong>18 e 36 meses</strong> de idade, período crítico para detecção precoce de sinais de TEA.</p>',
                    },
                    {
                        'titulo': 'Meus dados estão seguros?',
                        'conteudo': '<p>Sim! Seguimos rigorosamente a <strong>LGPD</strong> (Lei Geral de Proteção de Dados). Todos os vídeos, áudios e informações são criptografados e você tem controle total sobre seus dados.</p>',
                    },
                    {
                        'titulo': 'Quanto tempo leva a análise?',
                        'conteudo': '<p>O processamento pela IA geralmente leva entre <strong>30 minutos a 2 horas</strong>, dependendo da quantidade e tamanho dos arquivos enviados.</p>',
                    },
                    {
                        'titulo': 'O serviço é gratuito?',
                        'conteudo': '<p>Sim! O NEUROATHENA oferece triagem gratuita como parte de nosso compromisso com a democratização do acesso ao diagnóstico precoce de autismo.</p>',
                    },
                    {
                        'titulo': 'Preciso de equipamento especial?',
                        'conteudo': '<p>Não! Você pode usar apenas seu <strong>smartphone</strong> para gravar vídeos e áudios. O sistema aceita formatos comuns como MP4, AVI, MOV, MP3 e WAV.</p>',
                    },
                ]
            }),
        ]
        
        # Atualizar HomePage com os blocos
        self.home_page.body = homepage_content
        self.home_page.save()
        
        # Publicar revisão
        self.home_page.save_revision().publish()
        
        self.stdout.write('  ✓ HomePage configurada com todos os blocos!')
        self.stdout.write(f'  ✓ Total de blocos adicionados: {len(homepage_content)}')

    def create_noticias(self):
        """Cria notícias de demonstração."""
        categorias = list(CategoriaNoticias.objects.all())
        
        if not categorias:
            self.stdout.write(self.style.WARNING('  ! Nenhuma categoria encontrada, pulando notícias'))
            return
        
        if not self.noticias_index:
            self.stdout.write(self.style.WARNING('  ! NoticiasIndexPages não encontrada, pulando criação de notícias'))
            return
        
        noticias_data = [
            {
                'title': 'Athena alcança 95% de precisão em testes',
                'descricao': 'Novo sistema de IA demonstra alta eficácia na detecção precoce de sinais de autismo.',
                'categoria': 'Tecnologia',
            },
            {
                'title': 'Importância do diagnóstico precoce no autismo',
                'descricao': 'Estudos mostram que intervenção antes dos 3 anos pode melhorar significativamente o desenvolvimento.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Como funciona a análise multimodal de comportamento',
                'descricao': 'Entenda como o sistema combina vídeo, áudio e questionários para avaliação completa.',
                'categoria': 'Tecnologia',
            },
            {
                'title': 'Webinar gratuito sobre sinais precoces de autismo',
                'descricao': 'Participe do evento online com especialistas em desenvolvimento infantil.',
                'categoria': 'Comunidade',
            },
            {
                'title': 'Nova pesquisa revela padrões de comunicação em crianças autistas',
                'descricao': 'Estudo identifica marcadores linguísticos que podem auxiliar no diagnóstico.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Guia para pais: O que observar no desenvolvimento',
                'descricao': 'Orientações sobre marcos de desenvolvimento e quando buscar avaliação.',
                'categoria': 'Educação',
            },
            {
                'title': 'IA ajuda profissionais de saúde a identificar TEA',
                'descricao': 'Ferramenta auxilia pediatras e psicólogos na triagem inicial de autismo.',
                'categoria': 'Diagnóstico',
            },
            {
                'title': 'Resultados positivos em testes piloto do NEUROATHENA',
                'descricao': 'Sistema foi testado com 500 famílias apresentando resultados promissores.',
                'categoria': 'Pesquisa',
            },
            {
                'title': 'Acessibilidade no diagnóstico: democratizando o acesso',
                'descricao': 'Como a tecnologia pode levar triagem precoce para áreas remotas.',
                'categoria': 'Comunidade',
            },
            {
                'title': 'Privacidade e segurança no processamento de dados',
                'descricao': 'Conheça as medidas de proteção de dados sensíveis no sistema NEUROATHENA.',
                'categoria': 'Tecnologia',
            },
        ]
        
        for i, data in enumerate(noticias_data):
            # Verificar se notícia já existe
            if NoticiasPage.objects.filter(slug=f'noticia-{i+1}').exists():
                continue
            
            # Buscar categoria
            categoria = CategoriaNoticias.objects.filter(nome=data['categoria']).first()
            if not categoria:
                categoria = random.choice(categorias) if categorias else None
            
            try:
                # Criar notícia
                noticia = NoticiasPage(
                    title=data['title'],
                    slug=f'noticia-{i+1}',
                    locale=Locale.get_default(),
                    descricao=data['descricao'],
                    subtitle='',
                    categoria=categoria,
                    data_publicacao=timezone.now() - timedelta(days=random.randint(1, 30)),
                )
                
                # Adicionar imagem de destaque aleatória
                if self.demo_images:
                    noticia.imagem_destaque = random.choice(self.demo_images)
                
                # Adicionar ao índice de notícias
                self.noticias_index.add_child(instance=noticia)
                noticia.save_revision().publish()
                
                self.stdout.write(f'  ✓ Notícia: {data["title"][:50]}...')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ! Erro ao criar notícia: {e}'))
