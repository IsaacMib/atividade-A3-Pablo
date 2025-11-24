"""
Configuração global de fixtures do pytest para o projeto NeuroPrev.
Este arquivo é carregado automaticamente pelo pytest.
"""

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from wagtail.models import Page, Site, Locale
from faker import Faker

User = get_user_model()
faker = Faker('pt_BR')


# ==================== FIXTURES DE USUÁRIOS ====================

@pytest.fixture
def user_factory():
    """Factory para criar usuários de teste."""
    def make_user(**kwargs):
        defaults = {
            'username': faker.user_name(),
            'email': faker.email(),
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        
        password = defaults.pop('password')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def user(user_factory):
    """Usuário padrão para testes."""
    return user_factory()


@pytest.fixture
def responsavel(user_factory):
    """Usuário responsável (pai/mãe)."""
    user = user_factory(
        username='responsavel_test',
        email='responsavel@test.com'
    )
    from core.models import PerfilUsuario
    PerfilUsuario.objects.create(
        user=user,
        tipo_usuario='responsavel',
        telefone='(11) 98765-4321'
    )
    return user


@pytest.fixture
def profissional(user_factory):
    """Usuário profissional de saúde."""
    user = user_factory(
        username='profissional_test',
        email='profissional@test.com'
    )
    from core.models import PerfilUsuario
    PerfilUsuario.objects.create(
        user=user,
        tipo_usuario='profissional',
        telefone='(11) 91234-5678'
    )
    return user


@pytest.fixture
def admin_user(user_factory):
    """Usuário administrador."""
    return user_factory(
        username='admin',
        email='admin@test.com',
        is_staff=True,
        is_superuser=True
    )


# ==================== FIXTURES DO WAGTAIL ====================

@pytest.fixture
def root_page(db):
    """Página raiz do Wagtail."""
    root = Page.objects.get(depth=1)
    root.numchild = 0
    root.save()
    return root


@pytest.fixture
def site(db, root_page):
    """Site padrão do Wagtail."""
    site, created = Site.objects.get_or_create(
        is_default_site=True,
        defaults={
            'hostname': 'localhost',
            'port': 8000,
            'root_page': root_page,
            'site_name': 'NeuroPrev Test Site'
        }
    )
    return site


@pytest.fixture
def locale(db):
    """Locale padrão."""
    return Locale.get_default()


@pytest.fixture
def home_page(db, root_page, locale):
    """HomePage para testes."""
    from home.models import HomePage
    
    # Limpar páginas existentes
    for child in root_page.get_children():
        child.delete()
    
    home = HomePage(
        title="Home Test",
        slug="home",
        locale=locale
    )
    root_page.add_child(instance=home)
    home.save_revision().publish()
    return home


# ==================== FIXTURES DE REQUEST ====================

@pytest.fixture
def request_factory():
    """Factory de requests do Django."""
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory, user):
    """Request autenticado."""
    request = request_factory.get('/')
    request.user = user
    return request


# ==================== FIXTURES DE TRIAGEM ====================

@pytest.fixture
def questionario():
    """Questionário de teste (M-CHAT)."""
    from triagem_ia.models import Questionario
    return Questionario.objects.create(
        nome="M-CHAT-R/F",
        tipo="mchat",
        descricao="Modified Checklist for Autism in Toddlers, Revised with Follow-Up",
        faixa_etaria_minima=16,
        faixa_etaria_maxima=30,
        ativo=True
    )


@pytest.fixture
def perguntas(questionario):
    """Perguntas do questionário."""
    from triagem_ia.models import Pergunta
    
    perguntas_data = [
        {
            'ordem': 1,
            'texto': 'Se você aponta para alguma coisa do outro lado da sala, seu filho(a) olha para ela?',
            'tipo_resposta': 'sim_nao',
            'peso_risco': 2.0,
            'area_avaliada': 'Atenção Compartilhada'
        },
        {
            'ordem': 2,
            'texto': 'Você já se perguntou se seu filho(a) é surdo(a)?',
            'tipo_resposta': 'sim_nao',
            'peso_risco': 3.0,
            'area_avaliada': 'Comunicação'
        },
        {
            'ordem': 3,
            'texto': 'Seu filho(a) brinca de faz-de-conta?',
            'tipo_resposta': 'sim_nao',
            'peso_risco': 2.5,
            'area_avaliada': 'Jogo Simbólico'
        },
    ]
    
    return [
        Pergunta.objects.create(questionario=questionario, **data)
        for data in perguntas_data
    ]


@pytest.fixture
def triagem(responsavel, questionario):
    """Triagem de teste."""
    from triagem_ia.models import Triagem
    from datetime import date
    
    return Triagem.objects.create(
        responsavel=responsavel,
        questionario=questionario,
        nome_crianca="João da Silva",
        data_nascimento_crianca=date(2022, 6, 15),
        status='em_andamento',
        observacoes="Criança apresenta desenvolvimento típico."
    )


# ==================== FIXTURES DE PAINEL DIÁRIO ====================

@pytest.fixture
def crianca(responsavel):
    """Criança para testes."""
    from painel_diario.models import Crianca
    from datetime import date
    
    return Crianca.objects.create(
        responsavel=responsavel,
        nome="Maria da Silva",
        data_nascimento=date(2021, 3, 10),
        sexo='F',
        diagnostico_tea=False,
        ativo=True
    )


@pytest.fixture
def tipo_terapia():
    """Tipo de terapia para testes."""
    from painel_diario.models import TipoTerapia
    
    return TipoTerapia.objects.create(
        nome="ABA - Análise do Comportamento Aplicada",
        descricao="Terapia baseada em evidências para TEA",
        cor="#3498db",
        ativo=True
    )


@pytest.fixture
def registro_diario(crianca, responsavel):
    """Registro diário para testes."""
    from painel_diario.models import RegistroDiario
    from datetime import date
    
    return RegistroDiario.objects.create(
        crianca=crianca,
        data=date.today(),
        humor_geral='feliz',
        horas_sono=9.5,
        qualidade_sono='boa',
        alimentacao_adequada=True,
        iniciou_comunicacao=5,
        episodios_crise=0,
        comportamentos_repetitivos=False,
        interacao_outras_criancas=True,
        contato_visual='frequente',
        criado_por=responsavel
    )


# ==================== CONFIGURAÇÕES DE PYTEST ====================

def pytest_configure(config):
    """Configuração executada antes dos testes."""
    # Desabilitar migrationspara testes mais rápidos
    settings.MIGRATION_MODULES = {
        app: None for app in settings.INSTALLED_APPS
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Habilita acesso ao banco para todos os testes."""
    pass


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    """Configura storage temporário para media files nos testes."""
    settings.MEDIA_ROOT = tmpdir.strpath
