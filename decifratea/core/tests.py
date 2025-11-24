"""
Testes para o app Core.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import ConfiguracaoSistema, Log, ModelBase
from core.utils import (
    gerar_slug_unico,
    formatar_telefone,
    formatar_cpf,
    formatar_cnpj,
    truncar_texto,
)

User = get_user_model()


@pytest.mark.django_db
class TestConfiguracaoSistema(TestCase):
    """Testes para o model ConfiguracaoSistema"""

    def test_criar_configuracao(self):
        """Testa criação de configuração"""
        config = ConfiguracaoSistema.objects.create(
            nome_sistema="Teste",
            email_contato="teste@example.com"
        )
        assert config.nome_sistema == "Teste"
        assert config.email_contato == "teste@example.com"

    def test_singleton(self):
        """Testa que só pode existir uma configuração"""
        ConfiguracaoSistema.objects.create(nome_sistema="Config 1")
        
        with pytest.raises(Exception):
            ConfiguracaoSistema.objects.create(nome_sistema="Config 2")

    def test_get_config(self):
        """Testa método get_config"""
        config = ConfiguracaoSistema.get_config()
        assert config is not None
        assert isinstance(config, ConfiguracaoSistema)


@pytest.mark.django_db
class TestLog(TestCase):
    """Testes para o model Log"""

    def test_criar_log(self):
        """Testa criação de log"""
        log = Log.objects.create(
            tipo='INFO',
            acao='Teste de log',
            descricao='Descrição do teste'
        )
        assert log.tipo == 'INFO'
        assert log.acao == 'Teste de log'

    def test_registrar_log(self):
        """Testa método registrar"""
        log = Log.registrar(
            acao='Ação de teste',
            tipo='SUCCESS',
            descricao='Log criado via método registrar'
        )
        assert log.tipo == 'SUCCESS'
        assert Log.objects.count() == 1


class TestUtils(TestCase):
    """Testes para funções utilitárias"""

    def test_formatar_telefone(self):
        """Testa formatação de telefone"""
        assert formatar_telefone('11987654321') == '(11) 9 8765-4321'
        assert formatar_telefone('1133334444') == '(11) 3333-4444'

    def test_formatar_cpf(self):
        """Testa formatação de CPF"""
        assert formatar_cpf('12345678901') == '123.456.789-01'

    def test_formatar_cnpj(self):
        """Testa formatação de CNPJ"""
        assert formatar_cnpj('12345678000190') == '12.345.678/0001-90'

    def test_truncar_texto(self):
        """Testa truncamento de texto"""
        texto = "Este é um texto muito longo para testar"
        resultado = truncar_texto(texto, 20)
        assert len(resultado) <= 20
        assert resultado.endswith('...')
