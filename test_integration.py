#!/usr/bin/env python3
"""
Script de teste para verificar integração Django ↔ FastAPI
Simula o fluxo de análise sem precisar do servidor FastAPI rodando
"""

import os
import sys
import django
from pathlib import Path

# Setup Django - usar path dinâmico
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitepadrao.settings.testing')
django.setup()

from triagem_ia.models import (
    Questionario, Pergunta, Triagem, RespostaQuestionario, 
    ResultadoIA, AlertaIA
)
from painel_diario.models import Crianca, RegistroDiario, MidiaRegistroDiario
from django.contrib.auth import get_user_model

User = get_user_model()

def test_models_exist():
    """Testa se todos os models foram criados corretamente"""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Verificando Models Django")
    print("="*60)
    
    models_to_check = [
        ("Questionario", Questionario),
        ("Pergunta", Pergunta),
        ("Triagem", Triagem),
        ("RespostaQuestionario", RespostaQuestionario),
        ("ResultadoIA", ResultadoIA),
        ("AlertaIA", AlertaIA),
        ("Crianca", Crianca),
        ("RegistroDiario", RegistroDiario),
        ("MidiaRegistroDiario", MidiaRegistroDiario),
    ]
    
    for model_name, model_class in models_to_check:
        try:
            count = model_class.objects.count()
            print(f"✓ {model_name}: OK ({count} registros)")
        except Exception as e:
            print(f"✗ {model_name}: ERRO - {e}")
    
    print("="*60)

def test_create_triagem():
    """Testa criação de triagem completa"""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Criando Triagem de Teste")
    print("="*60)
    
    try:
        # 1. Criar usuário de teste
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        print(f"✓ Usuário criado/encontrado: {user.username}")
        
        # 2. Criar questionário
        questionario, created = Questionario.objects.get_or_create(
            nome="Questionário M-CHAT-R/F",
            defaults={
                'descricao': "Modified Checklist for Autism in Toddlers",
                'tipo': 'triagem',
                'faixa_etaria_minima': 16,  # meses
                'faixa_etaria_maxima': 30,  # meses
                'ativo': True,
            }
        )
        print(f"✓ Questionário: {questionario.nome} (ID: {questionario.id})")
        
        # 3. Criar perguntas
        if questionario.perguntas.count() == 0:
            perguntas_texto = [
                "Seu filho olha nos seus olhos quando você conversa com ele?",
                "Seu filho aponta para mostrar algo interessante?",
                "Seu filho brinca de faz-de-conta?",
            ]
            for i, texto in enumerate(perguntas_texto, 1):
                Pergunta.objects.create(
                    questionario=questionario,
                    texto=texto,
                    ordem=i,
                    tipo_resposta='sim_nao',
                    peso_risco=1.5,
                )
            print(f"✓ {len(perguntas_texto)} perguntas criadas")
        else:
            print(f"✓ Questionário já tem {questionario.perguntas.count()} perguntas")
        
        # 4. Criar triagem
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        data_nascimento = date.today() - relativedelta(months=36)
        triagem = Triagem.objects.create(
            responsavel=user,
            questionario=questionario,
            nome_crianca="João Silva",
            data_nascimento_crianca=data_nascimento,
            idade_meses=36,
            status='iniciada',
        )
        print(f"✓ Triagem criada: {triagem.nome_crianca} (ID: {triagem.id})")
        
        # 5. Criar respostas
        for pergunta in questionario.perguntas.all()[:3]:
            RespostaQuestionario.objects.create(
                triagem=triagem,
                pergunta=pergunta,
                resposta_numerica=0,  # 0 = não (risco)
                pontuacao_risco=pergunta.peso_risco,
            )
        print(f"✓ {triagem.respostas.count()} respostas criadas")
        
        # 6. Simular resultado de IA
        resultado = ResultadoIA.objects.create(
            triagem=triagem,
            probabilidade_tea=0.75,
            confianca='alta',
            score_texto=0.75,
            score_audio=0.7,
            score_video=0.8,
            areas_risco={
                'comunicacao': 0.8,
                'interacao_social': 0.85,
                'comportamento_repetitivo': 0.6,
            },
            recomendacoes="Recomenda-se avaliação diagnóstica especializada.",
            modelo_utilizado="NeuroPrev Multimodal v1.0",
            versao_modelo="1.0.0",
        )
        print(f"✓ ResultadoIA criado: Probabilidade TEA {resultado.probabilidade_tea:.2%} | Confiança {resultado.confianca}")
        
        # 7. Criar alertas
        alertas = [
            ("ausencia_contato_visual", "critico", "Ausência de contato visual detectada", "video", 0.9),
            ("estereotipia_motora", "atencao", "Movimentos repetitivos identificados", "video", 0.75),
            ("resposta_nome_ausente", "critico", "Criança não responde ao nome", "questionario", 1.0),
        ]
        for tipo, severidade, descricao, modalidade, confianca in alertas:
            AlertaIA.objects.create(
                resultado_ia=resultado,
                tipo_alerta=tipo,
                severidade=severidade,
                descricao=descricao,
                modalidade_origem=modalidade,
                confianca_deteccao=confianca,
            )
        print(f"✓ {len(alertas)} alertas criados")
        
        # 8. Atualizar triagem
        from django.utils import timezone
        triagem.nivel_risco = 'alto'
        triagem.status = 'concluida'
        triagem.pontuacao_total = resultado.probabilidade_tea
        triagem.concluida_em = timezone.now()
        triagem.save()
        print(f"✓ Triagem atualizada: Status {triagem.status}")
        
        print("\n📊 RESUMO DA TRIAGEM:")
        print(f"   • Criança: {triagem.nome_crianca} ({triagem.idade_meses} meses)")
        print(f"   • Questionário: {questionario.nome}")
        print(f"   • Respostas: {triagem.respostas.count()}")
        print(f"   • Probabilidade TEA: {resultado.probabilidade_tea:.2%}")
        print(f"   • Confiança: {resultado.confianca.upper()}")
        print(f"   • Score Texto: {resultado.score_texto}")
        print(f"   • Score Áudio: {resultado.score_audio}")
        print(f"   • Score Vídeo: {resultado.score_video}")
        print(f"   • Alertas: {resultado.alertas.count()}")
        
    except Exception as e:
        print(f"✗ ERRO ao criar triagem: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def test_services_import():
    """Testa se os services podem ser importados"""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Verificando Services Django")
    print("="*60)
    
    try:
        from triagem_ia.services import (
            AIAnalysisService, 
            TriagemAnalysisService,
            PainelDiarioAnalysisService,
        )
        print("✓ AIAnalysisService importado")
        print("✓ TriagemAnalysisService importado")
        print("✓ PainelDiarioAnalysisService importado")
        
        # Testar instanciação
        ai_service = AIAnalysisService()
        print(f"✓ AIAnalysisService instanciado (base_url: {ai_service.base_url})")
        
        triagem_service = TriagemAnalysisService()
        print("✓ TriagemAnalysisService instanciado")
        
        painel_service = PainelDiarioAnalysisService()
        print("✓ PainelDiarioAnalysisService instanciado")
        
    except Exception as e:
        print(f"✗ ERRO ao importar services: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def test_stats():
    """Mostra estatísticas do banco"""
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("="*60)
    
    stats = {
        "Usuários": User.objects.count(),
        "Questionários": Questionario.objects.count(),
        "Perguntas": Pergunta.objects.count(),
        "Triagens": Triagem.objects.count(),
        "Respostas": RespostaQuestionario.objects.count(),
        "Resultados IA": ResultadoIA.objects.count(),
        "Alertas IA": AlertaIA.objects.count(),
        "Crianças": Crianca.objects.count(),
        "Registros Diários": RegistroDiario.objects.count(),
        "Mídias": MidiaRegistroDiario.objects.count(),
    }
    
    for label, count in stats.items():
        print(f"   • {label}: {count}")
    
    print("="*60)

def main():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("🚀 TESTE DE INTEGRAÇÃO DJANGO - NeuroPrev AI")
    print("="*70)
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Django: {django.get_version()}")
    print(f"   Settings: {os.environ['DJANGO_SETTINGS_MODULE']}")
    print("="*70)
    
    # Executar testes
    test_models_exist()
    test_create_triagem()
    test_services_import()
    test_stats()
    
    print("\n" + "="*70)
    print("✅ TESTES CONCLUÍDOS!")
    print("="*70)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Configurar PostgreSQL (settings/dev.py)")
    print("   2. Configurar Celery + Redis para tarefas assíncronas")
    print("   3. Testar FastAPI server com modelos de IA reais")
    print("   4. Criar interface frontend para triagem")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
