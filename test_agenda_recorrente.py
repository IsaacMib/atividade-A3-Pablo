"""
Script de teste para verificar a atualização de título e slug de agendas recorrentes.

Execute com:
    workon codataSite && python test_agenda_recorrente.py
"""
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitepadrao.settings.dev')
sys.path.insert(0, '/home/gabriel/wagtail/site-padrao')
django.setup()

from datetime import date
from agenda.models import AgendaDoDiaPage, AgendaPage
from agenda.wagtail_hooks import atualizar_titulo_slug_agenda_recorrente

def testar_atualizacao_titulo_slug():
    """Testa a função atualizar_titulo_slug_agenda_recorrente"""
    
    print("=" * 60)
    print("TESTE: Atualização de Título e Slug - Agenda Recorrente")
    print("=" * 60)
    
    # Buscar uma AgendaPage existente como pai
    try:
        parent_page = AgendaPage.objects.first()
        if not parent_page:
            print("❌ ERRO: Nenhuma AgendaPage encontrada no sistema.")
            print("   Crie uma AgendaPage primeiro antes de executar este teste.")
            return
        
        print(f"\n✓ Página pai encontrada: {parent_page.title}")
        
        # ============================================================
        # TESTE 1: Criação inicial (is_new=True)
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE 1: CRIAÇÃO INICIAL (is_new=True)")
        print("=" * 60)
        
        test_page = AgendaDoDiaPage(
            title="Reunião com Secretários",
            slug="reuniao-com-secretarios",
            date=date(2025, 11, 20),
            habilitar_recorrencia=True,
            tipo_recorrencia='days',
            intervalo_recorrencia=7,  # Semanal
        )
        
        print("\nANTES da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        
        atualizar_titulo_slug_agenda_recorrente(test_page, parent_page)
        
        print("\nDEPOIS da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        
        # Guardar valores para o próximo teste
        titulo_criacao = test_page.title
        slug_criacao = test_page.slug
        
        # ============================================================
        # TESTE 2: Mudança de data (simulando edição)
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE 2: MUDANÇA DE DATA (is_new=False)")
        print("=" * 60)
        
        # Simular que o usuário mudou a data
        test_page.date = date(2025, 11, 27)  # Nova data
        
        print("\nANTES da atualização (com data mudada):")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        print(f"  Data: {test_page.date}")
        
        atualizar_titulo_slug_agenda_recorrente(test_page, parent_page)
        
        print("\nDEPOIS da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        
        # ============================================================
        # TESTE 3: Mudança de tipo de recorrência
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE 3: MUDANÇA DE TIPO DE RECORRÊNCIA (is_new=False)")
        print("=" * 60)
        
        # Simular que o usuário mudou o tipo de recorrência
        test_page.tipo_recorrencia = 'months'  # Mensal
        test_page.intervalo_recorrencia = 1
        
        print("\nANTES da atualização (com tipo mudado):")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        print(f"  Tipo: {test_page.get_tipo_recorrencia_display()}")
        
        atualizar_titulo_slug_agenda_recorrente(test_page, parent_page)
        
        print("\nDEPOIS da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        
        # ============================================================
        # VERIFICAÇÕES FINAIS
        # ============================================================
        print("\n" + "=" * 60)
        print("VERIFICAÇÕES FINAIS:")
        print("=" * 60)
        
        checks = []
        
        # 1. Título deve sempre conter o nome do pai
        if parent_page.title in test_page.title:
            checks.append(("✓", f"Título contém nome do pai '{parent_page.title}'"))
        else:
            checks.append(("✗", "Título NÃO contém nome do pai"))
        
        # 2. Slug deve conter o slug do pai
        if parent_page.slug in test_page.slug:
            checks.append(("✓", f"Slug contém slug do pai '{parent_page.slug}'"))
        else:
            checks.append(("✗", "Slug NÃO contém slug do pai"))
        
        # 3. Título deve refletir tipo atual (Mensal)
        if "Mensal" in test_page.title:
            checks.append(("✓", "Título reflete tipo atual 'Mensal'"))
        else:
            checks.append(("✗", "Título NÃO reflete tipo atual"))
        
        # 4. Slug deve refletir tipo atual
        if "mensal" in test_page.slug:
            checks.append(("✓", "Slug reflete tipo atual 'mensal'"))
        else:
            checks.append(("✗", "Slug NÃO reflete tipo atual"))
        
        # 5. Título deve refletir data atual
        if "27 de novembro" in test_page.title:
            checks.append(("✓", "Título reflete data atual '27 de novembro'"))
        else:
            checks.append(("✗", f"Título NÃO reflete data atual (tem: {test_page.title})"))
        
        # 6. Slug deve refletir data atual
        if "2025-11-27" in test_page.slug:
            checks.append(("✓", "Slug reflete data atual '2025-11-27'"))
        else:
            checks.append(("✗", f"Slug NÃO reflete data atual (tem: {test_page.slug})"))
        
        # 7. NÃO deve ter sufixos duplicados
        count_recorrente = test_page.title.count("Agenda Recorrente")
        if count_recorrente == 1:
            checks.append(("✓", "Título NÃO tem sufixos duplicados"))
        else:
            checks.append(("✗", f"Título tem 'Agenda Recorrente' {count_recorrente} vezes"))
        
        # Imprimir resultados
        for simbolo, mensagem in checks:
            print(f"{simbolo} {mensagem}")
        
        # Resultado final
        total_checks = len(checks)
        checks_ok = sum(1 for s, _ in checks if s == "✓")
        
        print("\n" + "=" * 60)
        if checks_ok == total_checks:
            print(f"✓ TODOS OS TESTES PASSARAM! ({checks_ok}/{total_checks} verificações)")
        else:
            print(f"✗ ALGUNS TESTES FALHARAM! ({checks_ok}/{total_checks} verificações)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO ao executar teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_atualizacao_titulo_slug()
