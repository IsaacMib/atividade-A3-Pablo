"""
Testes unitários para os modelos do app painel_diario.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from painel_diario.models import (
    Crianca, RegistroDiario, MidiaRegistroDiario,
    TipoTerapia, SessaoTerapia
)


# ==================== TESTES DE CRIANCA ====================

@pytest.mark.django_db
class TestCrianca:
    """Testes para o modelo Crianca."""
    
    def test_criar_crianca_basica(self, responsavel):
        """Testa criação de criança básica."""
        crianca = Crianca.objects.create(
            responsavel=responsavel,
            nome="Pedro Santos",
            data_nascimento=date(2020, 5, 10),
            sexo='M',
            diagnostico_tea=False
        )
        
        assert crianca.nome == "Pedro Santos"
        assert crianca.sexo == 'M'
        assert crianca.diagnostico_tea is False
        assert crianca.ativo is True
    
    def test_crianca_com_diagnostico(self, responsavel):
        """Testa criança com diagnóstico de TEA."""
        crianca = Crianca.objects.create(
            responsavel=responsavel,
            nome="Ana Silva",
            data_nascimento=date(2019, 3, 15),
            sexo='F',
            diagnostico_tea=True,
            data_diagnostico=date(2021, 6, 20),
            observacoes_gerais="Diagnóstico confirmado por equipe multidisciplinar"
        )
        
        assert crianca.diagnostico_tea is True
        assert crianca.data_diagnostico == date(2021, 6, 20)
        assert "multidisciplinar" in crianca.observacoes_gerais
    
    def test_calcular_idade(self, crianca):
        """Testa cálculo de idade."""
        from freezegun import freeze_time
        
        # Criança nascida em 2021-03-10
        with freeze_time("2024-11-24"):
            idade = crianca.calcular_idade()
            assert idade['anos'] == 3
            assert idade['meses'] == 8
    
    def test_idade_display(self, crianca):
        """Testa formatação de exibição da idade."""
        from freezegun import freeze_time
        
        with freeze_time("2024-11-10"):
            display = crianca.idade_display()
            assert "3 anos" in display
            assert "8 meses" in display
    
    def test_crianca_str(self, crianca):
        """Testa representação em string."""
        assert str(crianca) == "Maria da Silva"
    
    def test_crianca_ordering(self, responsavel):
        """Testa ordenação por nome."""
        c1 = Crianca.objects.create(
            responsavel=responsavel,
            nome="Zilda",
            data_nascimento=date(2020, 1, 1),
            sexo='F'
        )
        c2 = Crianca.objects.create(
            responsavel=responsavel,
            nome="Ana",
            data_nascimento=date(2020, 1, 1),
            sexo='F'
        )
        
        criancas = list(Crianca.objects.all())
        # Ana deve vir antes de Zilda
        nomes = [c.nome for c in criancas if c.nome in ['Ana', 'Zilda']]
        assert nomes == ['Ana', 'Zilda']


# ==================== TESTES DE REGISTRO DIARIO ====================

@pytest.mark.django_db
class TestRegistroDiario:
    """Testes para o modelo RegistroDiario."""
    
    def test_criar_registro_completo(self, crianca, responsavel):
        """Testa criação de registro diário completo."""
        registro = RegistroDiario.objects.create(
            crianca=crianca,
            data=date.today(),
            humor_geral='neutro',
            horas_sono=Decimal('10.5'),
            qualidade_sono='boa',
            alimentacao_adequada=True,
            observacoes_alimentacao='Frutas, legumes, proteínas',
            iniciou_comunicacao=8,
            palavras_novas='mamãe, papai, água',
            episodios_crise=0,
            comportamentos_repetitivos=False,
            interacao_outras_criancas=True,
            contato_visual='frequente',
            atividades_realizadas='Brincadeiras livres, parque, leitura',
            conquistas_dia='Tentou amarrar sapato sozinha',
            observacoes='Dia tranquilo e produtivo',
            criado_por=responsavel
        )
        
        assert registro.humor_geral == 'neutro'
        assert registro.horas_sono == Decimal('10.5')
        assert registro.iniciou_comunicacao == 8
        assert registro.contato_visual == 'frequente'
    
    def test_registro_unico_por_dia(self, crianca, responsavel):
        """Testa constraint de registro único por criança/dia."""
        hoje = date.today()
        
        RegistroDiario.objects.create(
            crianca=crianca,
            data=hoje,
            humor_geral='feliz',
            criado_por=responsavel
        )
        
        # Tentar criar outro registro para mesma criança/data
        with pytest.raises(IntegrityError):
            RegistroDiario.objects.create(
                crianca=crianca,
                data=hoje,
                humor_geral='triste',
                criado_por=responsavel
            )
    
    def test_horas_sono_validas(self, crianca, responsavel):
        """Testa validação de horas de sono (0-24)."""
        # Valor válido
        r1 = RegistroDiario(
            crianca=crianca,
            data=date.today(),
            humor_geral='neutro',
            horas_sono=Decimal('12.5'),
            criado_por=responsavel
        )
        r1.full_clean()  # Não deve lançar exceção
        
        # Valor inválido (maior que 24)
        r2 = RegistroDiario(
            crianca=crianca,
            data=date.today() - timedelta(days=1),
            humor_geral='feliz',
            horas_sono=Decimal('25.0'),
            criado_por=responsavel
        )
        
        with pytest.raises(ValidationError):
            r2.full_clean()
    
    def test_registro_str(self, registro_diario):
        """Testa representação em string."""
        str_repr = str(registro_diario)
        assert "Maria da Silva" in str_repr or "Registro" in str_repr
    
    def test_registro_ordering(self, crianca, responsavel):
        """Testa ordenação por criança e data descendente."""
        r1 = RegistroDiario.objects.create(
            crianca=crianca,
            data=date.today() - timedelta(days=2),
            criado_por=responsavel
        )
        r2 = RegistroDiario.objects.create(
            crianca=crianca,
            data=date.today(),
            criado_por=responsavel
        )
        
        registros = list(RegistroDiario.objects.all())
        # Mais recente deve vir primeiro
        assert registros[0].data > registros[-1].data


# ==================== TESTES DE MIDIA REGISTRO DIARIO ====================

@pytest.mark.django_db
class TestMidiaRegistroDiario:
    """Testes para o modelo MidiaRegistroDiario."""
    
    def test_criar_midia_foto(self, registro_diario):
        """Testa criação de mídia do tipo foto."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        foto = SimpleUploadedFile(
            "test_foto.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        midia = MidiaRegistroDiario.objects.create(
            registro=registro_diario,
            tipo='foto',
            arquivo=foto,
            descricao='Criança brincando no parque'
        )
        
        assert midia.tipo == 'foto'
        assert 'Criança brincando' in midia.descricao
        assert midia.analisado_ia is False
    
    def test_criar_midia_video_com_analise(self, registro_diario):
        """Testa criação de vídeo com análise de IA."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        video = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        midia = MidiaRegistroDiario.objects.create(
            registro=registro_diario,
            tipo='video',
            arquivo=video,
            duracao_segundos=120,
            analisado_ia=True,
            resultado_analise={
                'contato_visual': 0.65,
                'expressao_facial': 0.70,
                'movimentos_repetitivos': False
            }
        )
        
        assert midia.tipo == 'video'
        assert midia.duracao_segundos == 120
        assert midia.analisado_ia is True
        assert 'contato_visual' in midia.resultado_analise
    
    def test_midia_str(self, registro_diario):
        """Testa representação em string."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        audio = SimpleUploadedFile("test.mp3", b"audio")
        
        midia = MidiaRegistroDiario.objects.create(
            registro=registro_diario,
            tipo='audio',
            arquivo=audio,
            descricao='Teste de áudio'
        )
        
        str_repr = str(midia)
        assert 'audio' in str_repr.lower() or 'áudio' in str_repr.lower()


# ==================== TESTES DE TIPO TERAPIA ====================

@pytest.mark.django_db
class TestTipoTerapia:
    """Testes para o modelo TipoTerapia."""
    
    def test_criar_tipo_terapia(self):
        """Testa criação de tipo de terapia."""
        tipo = TipoTerapia.objects.create(
            nome="Fonoaudiologia",
            descricao="Terapia para desenvolvimento da fala e linguagem",
            cor="#e74c3c",
            ativo=True
        )
        
        assert tipo.nome == "Fonoaudiologia"
        assert tipo.cor == "#e74c3c"
        assert tipo.ativo is True
    
    def test_tipo_terapia_str(self, tipo_terapia):
        """Testa representação em string."""
        assert str(tipo_terapia) == "ABA - Análise do Comportamento Aplicada"
    
    def test_tipo_terapia_ordering(self):
        """Testa ordenação por nome."""
        t1 = TipoTerapia.objects.create(
            nome="Terapia Ocupacional",
            cor="#3498db"
        )
        t2 = TipoTerapia.objects.create(
            nome="Fonoaudiologia",
            cor="#e74c3c"
        )
        
        tipos = list(TipoTerapia.objects.all())
        nomes = [t.nome for t in tipos if 'Terapia' in t.nome or 'Fono' in t.nome]
        assert nomes[0] < nomes[1]  # Ordem alfabética


# ==================== TESTES DE SESSAO TERAPIA ====================

@pytest.mark.django_db
class TestSessaoTerapia:
    """Testes para o modelo SessaoTerapia."""
    
    def test_criar_sessao_basica(self, crianca, tipo_terapia, profissional):
        """Testa criação de sessão básica."""
        sessao = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime(2024, 11, 24, 14, 0),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            objetivos_sessao='Trabalhar atenção compartilhada',
            atividades_realizadas='Jogos de encaixe, quebra-cabeças',
            progressos_observados='Melhor foco nas atividades',
            avaliacao_geral=4,
            engajamento_crianca=4,
            criado_por=profissional
        )
        
        assert sessao.duracao_minutos == 60
        assert sessao.presenca == 'presente'
        assert sessao.avaliacao_geral == 4
        assert sessao.engajamento_crianca == 4
    
    def test_sessao_com_tarefa_casa(self, crianca, tipo_terapia, profissional):
        """Testa sessão com tarefas de casa."""
        proxima_sessao = datetime.now() + timedelta(days=7)
        
        sessao = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime.now(),
            duracao_minutos=45,
            profissional_nome=profissional.username,
            presenca='presente',
            tarefas_casa='Praticar contato visual durante refeições',
            proxima_sessao=proxima_sessao,
            criado_por=profissional
        )
        
        assert 'contato visual' in sessao.tarefas_casa
        assert sessao.proxima_sessao == proxima_sessao
    
    def test_avaliacoes_range(self, crianca, tipo_terapia, profissional):
        """Testa validação de avaliações (1-5)."""
        # Valor válido
        s1 = SessaoTerapia(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime.now(),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            avaliacao_geral=5,
            engajamento_crianca=1,
            criado_por=profissional
        )
        s1.full_clean()  # Não deve lançar exceção
        
        # Valor inválido (maior que 5)
        s2 = SessaoTerapia(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime.now(),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            avaliacao_geral=6,  # Inválido
            criado_por=profissional
        )
        
        with pytest.raises(ValidationError):
            s2.full_clean()
    
    def test_sessao_cancelada(self, crianca, tipo_terapia, profissional):
        """Testa registro de sessão cancelada."""
        sessao = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime(2024, 11, 20, 10, 0),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='cancelada',
            observacoes_responsavel='Criança com febre',
            criado_por=profissional
        )
        
        assert sessao.presenca == 'cancelada'
        assert 'febre' in sessao.observacoes_responsavel
    
    def test_sessao_str(self, crianca, tipo_terapia, profissional):
        """Testa representação em string."""
        sessao = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime(2024, 11, 24, 15, 30),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            criado_por=profissional
        )
        
        str_repr = str(sessao)
        assert "Maria da Silva" in str_repr
        assert "ABA" in str_repr
        assert "24/11/2024" in str_repr
    
    def test_sessao_ordering(self, crianca, tipo_terapia, profissional):
        """Testa ordenação por data descendente."""
        s1 = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime.now() - timedelta(days=7),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            criado_por=profissional
        )
        s2 = SessaoTerapia.objects.create(
            crianca=crianca,
            tipo_terapia=tipo_terapia,
            data_hora=datetime.now(),
            duracao_minutos=60,
            profissional_nome=profissional.username,
            presenca='presente',
            criado_por=profissional
        )
        
        sessoes = list(SessaoTerapia.objects.all())
        # Mais recente deve vir primeiro
        assert sessoes[0].data_hora > sessoes[-1].data_hora
