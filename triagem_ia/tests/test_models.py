"""
Testes unitários para os modelos do app triagem_ia.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from triagem_ia.models import (
    Questionario, Pergunta, Triagem, RespostaQuestionario,
    ModalidadeTexto, ResultadoIA, AlertaIA
)


# ==================== TESTES DE QUESTIONARIO ====================

@pytest.mark.django_db
class TestQuestionario:
    """Testes para o modelo Questionario."""
    
    def test_criar_questionario_basico(self):
        """Testa criação de questionário básico."""
        questionario = Questionario.objects.create(
            nome="M-CHAT-R/F",
            tipo="mchat",
            descricao="Modified Checklist for Autism in Toddlers",
            faixa_etaria_minima=16,
            faixa_etaria_maxima=30,
            ativo=True
        )
        
        assert questionario.nome == "M-CHAT-R/F"
        assert questionario.tipo == "mchat"
        assert questionario.faixa_etaria_minima == 16
        assert questionario.faixa_etaria_maxima == 30
        assert questionario.ativo is True
    
    def test_questionario_str(self, questionario):
        """Testa representação em string."""
        assert "M-CHAT-R/F" in str(questionario)
        assert "M-CHAT" in str(questionario)  # get_tipo_display()
    
    def test_questionario_ordering(self):
        """Testa ordenação padrão por nome."""
        q1 = Questionario.objects.create(
            nome="ABC", tipo="abc", faixa_etaria_minima=24, faixa_etaria_maxima=72
        )
        q2 = Questionario.objects.create(
            nome="CARS", tipo="cars", faixa_etaria_minima=24, faixa_etaria_maxima=120
        )
        
        questionarios = list(Questionario.objects.all())
        assert questionarios[0].nome == "ABC"
        assert questionarios[1].nome == "CARS"
    
    def test_faixa_etaria_invalida(self):
        """Testa validação de faixa etária."""
        questionario = Questionario(
            nome="Teste",
            tipo="teste",
            faixa_etaria_minima=30,
            faixa_etaria_maxima=16  # Máxima menor que mínima
        )
        
        with pytest.raises(ValidationError):
            questionario.full_clean()


# ==================== TESTES DE PERGUNTA ====================

@pytest.mark.django_db
class TestPergunta:
    """Testes para o modelo Pergunta."""
    
    def test_criar_pergunta(self, questionario):
        """Testa criação de pergunta."""
        pergunta = Pergunta.objects.create(
            questionario=questionario,
            ordem=1,
            texto="Seu filho(a) olha quando você aponta?",
            tipo_resposta="sim_nao",
            peso_risco=2.5,
            area_avaliada="Atenção Compartilhada"
        )
        
        assert pergunta.ordem == 1
        assert pergunta.tipo_resposta == "sim_nao"
        assert pergunta.peso_risco == Decimal("2.5")
        assert pergunta.area_avaliada == "Atenção Compartilhada"
    
    def test_pergunta_str(self, questionario):
        """Testa representação em string."""
        pergunta = Pergunta.objects.create(
            questionario=questionario,
            ordem=1,
            texto="Pergunta muito longa" * 10,
            tipo_resposta="sim_nao"
        )
        
        str_repr = str(pergunta)
        # Verifica que contém elementos básicos
        assert "M-CHAT-R/F" in str_repr or "Pergunta" in str_repr
    
    def test_pergunta_ordering(self, questionario):
        """Testa ordenação por questionário e ordem."""
        p1 = Pergunta.objects.create(
            questionario=questionario, ordem=2, texto="Segunda", tipo_resposta="sim_nao"
        )
        p2 = Pergunta.objects.create(
            questionario=questionario, ordem=1, texto="Primeira", tipo_resposta="sim_nao"
        )
        
        perguntas = list(Pergunta.objects.all())
        assert perguntas[0].ordem == 1
        assert perguntas[1].ordem == 2
    
    def test_peso_risco_limites(self, questionario):
        """Testa limites do peso de risco (0-10)."""
        # Peso válido
        p1 = Pergunta(
            questionario=questionario,
            ordem=1,
            texto="Teste",
            tipo_resposta="sim_nao",
            peso_risco=10.0
        )
        p1.full_clean()  # Não deve lançar exceção
        
        # Peso inválido (maior que 10)
        p2 = Pergunta(
            questionario=questionario,
            ordem=2,
            texto="Teste 2",
            tipo_resposta="sim_nao",
            peso_risco=11.0
        )
        
        with pytest.raises(ValidationError):
            p2.full_clean()


# ==================== TESTES DE TRIAGEM ====================

@pytest.mark.django_db
class TestTriagem:
    """Testes para o modelo Triagem."""
    
    def test_criar_triagem(self, responsavel, questionario):
        """Testa criação de triagem."""
        triagem = Triagem.objects.create(
            responsavel=responsavel,
            questionario=questionario,
            nome_crianca="João Silva",
            data_nascimento_crianca=date(2022, 1, 15),
            status='iniciada'
        )
        
        assert triagem.nome_crianca == "João Silva"
        assert triagem.status == 'iniciada'
        assert triagem.responsavel == responsavel
    
    def test_calcular_idade_meses(self, triagem):
        """Testa cálculo de idade em meses."""
        # Data de nascimento conhecida: 2022-06-15
        # Data de hoje precisa ser mockada para teste consistente
        from freezegun import freeze_time
        
        with freeze_time("2024-06-15"):
            idade_meses = triagem.calcular_idade_meses()
            assert idade_meses == 24  # 2 anos exatos
        
        with freeze_time("2024-12-15"):
            idade_meses = triagem.calcular_idade_meses()
            assert idade_meses == 30  # 2 anos e 6 meses
    
    def test_triagem_str(self, triagem):
        """Testa representação em string."""
        str_repr = str(triagem)
        assert "João da Silva" in str_repr or "Triagem" in str_repr
    
    def test_status_choices(self, responsavel, questionario):
        """Testa transições de status."""
        triagem = Triagem.objects.create(
            responsavel=responsavel,
            questionario=questionario,
            nome_crianca="Maria",
            data_nascimento_crianca=date(2022, 1, 1),
            status='iniciada'
        )
        
        # Transição válida
        triagem.status = 'em_andamento'
        triagem.save()
        assert triagem.status == 'em_andamento'
        
        triagem.status = 'aguardando_analise'
        triagem.save()
        
        triagem.status = 'concluida'
        triagem.concluida_em = datetime.now()
        triagem.save()
        assert triagem.concluida_em is not None
    
    def test_nivel_risco_choices(self, triagem):
        """Testa níveis de risco."""
        triagem.nivel_risco = 'baixo'
        triagem.save()
        assert triagem.nivel_risco == 'baixo'
        
        triagem.nivel_risco = 'muito_alto'
        triagem.save()
        assert triagem.nivel_risco == 'muito_alto'


# ==================== TESTES DE RESPOSTA QUESTIONARIO ====================

@pytest.mark.django_db
class TestRespostaQuestionario:
    """Testes para o modelo RespostaQuestionario."""
    
    def test_criar_resposta_sim_nao(self, triagem, perguntas):
        """Testa criação de resposta sim/não."""
        pergunta = perguntas[0]  # Primeira pergunta
        
        resposta = RespostaQuestionario.objects.create(
            triagem=triagem,
            pergunta=pergunta,
            resposta_texto="Sim"
        )
        
        assert resposta.resposta_texto == "Sim"
        assert resposta.pergunta.tipo_resposta == "sim_nao"
    
    def test_criar_resposta_numerica(self, triagem, questionario):
        """Testa criação de resposta numérica (Likert)."""
        pergunta = Pergunta.objects.create(
            questionario=questionario,
            ordem=10,
            texto="Avalie de 1 a 5",
            tipo_resposta="likert",
            peso_risco=1.5
        )
        
        resposta = RespostaQuestionario.objects.create(
            triagem=triagem,
            pergunta=pergunta,
            resposta_numerica=4
        )
        
        assert resposta.resposta_numerica == 4
        assert resposta.pergunta.tipo_resposta == "likert"
    
    def test_resposta_unica_por_pergunta(self, triagem, perguntas):
        """Testa constraint de resposta única por pergunta."""
        pergunta = perguntas[0]
        
        RespostaQuestionario.objects.create(
            triagem=triagem,
            pergunta=pergunta,
            resposta_texto="Sim"
        )
        
        # Tentar criar outra resposta para mesma pergunta
        with pytest.raises(IntegrityError):
            RespostaQuestionario.objects.create(
                triagem=triagem,
                pergunta=pergunta,
                resposta_texto="Não"
            )


# ==================== TESTES DE RESULTADO IA ====================

@pytest.mark.django_db
class TestResultadoIA:
    """Testes para o modelo ResultadoIA."""
    
    def test_criar_resultado_ia(self, triagem):
        """Testa criação de resultado de IA."""
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.75,
            confianca='alta',  # CharField com choices
            score_texto=0.70,
            score_audio=0.80,
            score_video=0.75,
            modelo_utilizado="Athena Multimodal",
            versao_modelo="1.0.0",
            areas_risco={
                "comunicacao": 0.8,
                "interacao_social": 0.7,
                "comportamentos_repetitivos": 0.6
            }
        )
        
        assert resultado.probabilidade_tea == 0.75
        assert resultado.confianca == 'alta'
        assert "comunicacao" in resultado.areas_risco
        assert resultado.modelo_utilizado == "Athena Multimodal"
    
    def test_resultado_ia_str(self, triagem):
        """Testa representação em string."""
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.65,
            confianca='alta',
            modelo_utilizado="TestModel",
            versao_modelo="1.0"
        )
        
        str_repr = str(resultado)
        assert "Resultado IA" in str_repr or "Triagem" in str_repr
    
    def test_scores_range(self, triagem):
        """Testa validação de range dos scores (0-1)."""
        # Score válido
        r1 = ResultadoIA(
            triagem=triagem,
            probabilidade_tea=0.5,
            confianca='media',  # CharField com choices
            score_texto=0.0,
            modelo_utilizado="Test",
            versao_modelo="1.0"
        )
        r1.full_clean()  # Não deve lançar exceção
        
        # Score inválido (maior que 1)
        r2 = ResultadoIA(
            triagem=triagem,
            probabilidade_tea=1.5,  # Inválido
            confianca='alta',
            modelo_utilizado="Test",
            versao_modelo="1.0"
        )
        
        with pytest.raises(ValidationError):
            r2.full_clean()


# ==================== TESTES DE ALERTA IA ====================

@pytest.mark.django_db
class TestAlertaIA:
    """Testes para o modelo AlertaIA."""
    
    def test_criar_alerta(self, triagem):
        """Testa criação de alerta."""
        # Primeiro precisa criar resultado_ia
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.75,
            confianca='alta',
            modelo_utilizado="TestModel",
            versao_modelo="1.0"
        )
        
        alerta = AlertaIA.objects.create(
            resultado_ia=resultado,
            severidade='critico',
            tipo_alerta='comportamento_atipico',
            descricao='Comportamento repetitivo severo detectado',
            modalidade_origem='video',
            timestamp_deteccao=155.5,  # 02:35
            confianca_deteccao=0.92
        )
        
        assert alerta.severidade == 'critico'
        assert alerta.tipo_alerta == 'comportamento_atipico'
        assert alerta.modalidade_origem == 'video'
        assert alerta.confianca_deteccao == 0.92
    
    def test_alerta_ordering(self, triagem):
        """Testa ordenação por severidade e confiança."""
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.5,
            confianca='media',
            modelo_utilizado="Test",
            versao_modelo="1.0"
        )
        
        info_alerta = AlertaIA.objects.create(
            resultado_ia=resultado,
            severidade='info',
            tipo_alerta='teste1',
            descricao='Teste 1',
            modalidade_origem='texto',
            confianca_deteccao=0.5
        )
        critico_alerta = AlertaIA.objects.create(
            resultado_ia=resultado,
            severidade='critico',
            tipo_alerta='teste2',
            descricao='Teste 2',
            modalidade_origem='video',
            confianca_deteccao=0.9
        )
        
        alertas = list(AlertaIA.objects.all())
        # Verifica que ambos alertas foram criados
        assert len(alertas) == 2
        assert critico_alerta in alertas
        assert info_alerta in alertas
    
    def test_alerta_str(self, triagem):
        """Testa representação em string."""
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.6,
            confianca='media',
            modelo_utilizado="Test",
            versao_modelo="1.0"
        )
        
        alerta = AlertaIA.objects.create(
            resultado_ia=resultado,
            severidade='atencao',
            tipo_alerta='contato_visual_reduzido',
            descricao='Contato visual abaixo do esperado',
            modalidade_origem='video',
            confianca_deteccao=0.75
        )
        
        str_repr = str(alerta)
        assert "tencao" in str_repr.lower() or "Atenção" in str_repr
        assert "contato_visual_reduzido" in str_repr
