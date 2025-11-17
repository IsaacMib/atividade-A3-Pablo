"""
Script de teste para verificar a atualização de título e slug de agendas NORMAIS (sem recorrência).

Execute com:
    workon codataSite && python test_agenda_normal.py
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
from agenda.wagtail_hooks import atualizar_titulo_slug_agenda_normal

def testar_agenda_normal():
    """Testa a função atualizar_titulo_slug_agenda_normal"""
    
    print("=" * 60)
    print("TESTE: Atualização de Título e Slug - Agenda NORMAL")
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
        # TESTE 1: Criação de agenda normal
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE 1: CRIAÇÃO DE AGENDA NORMAL")
        print("=" * 60)
        
        test_page = AgendaDoDiaPage(
            title="Agenda Qualquer",  # Título que o usuário digita
            slug="agenda-qualquer",
            date=date(2025, 11, 20),
            habilitar_recorrencia=False,  # SEM recorrência
            tipo_recorrencia='none',
        )
        
        print("\nANTES da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        print(f"  Data: {test_page.date}")
        print(f"  Recorrência: {test_page.habilitar_recorrencia}")
        
        atualizar_titulo_slug_agenda_normal(test_page, parent_page)
        
        print("\nDEPOIS da atualização:")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        
        # ============================================================
        # TESTE 2: Mudança de data em agenda normal
        # ============================================================
        print("\n" + "=" * 60)
        print("TESTE 2: MUDANÇA DE DATA EM AGENDA NORMAL")
        print("=" * 60)
        
        # Simular que o usuário mudou a data
        test_page.date = date(2025, 12, 15)
        
        print("\nANTES da atualização (com data mudada):")
        print(f"  Título: {test_page.title}")
        print(f"  Slug: {test_page.slug}")
        print(f"  Data: {test_page.date}")
        
        atualizar_titulo_slug_agenda_normal(test_page, parent_page)
        
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
        
        # 1. Título deve conter o nome do pai
        if parent_page.title in test_page.title:
            checks.append(("✓", f"Título contém nome do pai '{parent_page.title}'"))
        else:
            checks.append(("✗", "Título NÃO contém nome do pai"))
        
        # 2. Slug deve conter o slug do pai
        if parent_page.slug in test_page.slug:
            checks.append(("✓", f"Slug contém slug do pai '{parent_page.slug}'"))
        else:
            checks.append(("✗", "Slug NÃO contém slug do pai"))
        
        # 3. Título deve ter "Agenda do Dia"
        if "Agenda do Dia" in test_page.title:
            checks.append(("✓", "Título contém 'Agenda do Dia'"))
        else:
            checks.append(("✗", "Título NÃO contém 'Agenda do Dia'"))
        
        # 4. Título deve refletir data atual (15 de dezembro)
        if "15 de dezembro de 2025" in test_page.title:
            checks.append(("✓", "Título reflete data atual '15 de dezembro de 2025'"))
        else:
            checks.append(("✗", f"Título NÃO reflete data atual (tem: {test_page.title})"))
        
        # 5. Slug deve refletir data atual
        if "2025-12-15" in test_page.slug:
            checks.append(("✓", "Slug reflete data atual '2025-12-15'"))
        else:
            checks.append(("✗", f"Slug NÃO reflete data atual (tem: {test_page.slug})"))
        
        # 6. Título NÃO deve ter "Recorrente"
        if "Recorrente" not in test_page.title:
            checks.append(("✓", "Título NÃO contém 'Recorrente' (correto para agenda normal)"))
        else:
            checks.append(("✗", "Título contém 'Recorrente' (incorreto!)"))
        
        # 7. Slug deve ter formato simples (sem -recorrente-)
        if "-recorrente-" not in test_page.slug:
            checks.append(("✓", "Slug NÃO contém '-recorrente-' (correto para agenda normal)"))
        else:
            checks.append(("✗", "Slug contém '-recorrente-' (incorreto!)"))
        
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
    testar_agenda_normal()
