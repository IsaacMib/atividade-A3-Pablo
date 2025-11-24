#!/usr/bin/env python
"""Script para configurar HomePage com todos os blocos."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitepadrao.settings.base')
django.setup()

from home.models import HomePage
from wagtail.models import Site, Locale

# Obter root e site
site = Site.objects.first()
root = site.root_page

# Verificar se já existe HomePage
home_page = HomePage.objects.first()

if not home_page:
    print("Criando HomePage...")
    
    # Remover filhos da root se houver
    for child in root.get_children():
        print(f"Removendo: {child.title}")
        child.delete()
    
    # Resetar numchild se necessário
    root.numchild = 0
    root.save()
    root.refresh_from_db()
    
    # Criar HomePage
    locale = Locale.get_default()
    home_page = HomePage(
        title='NeuroPrev - Triagem Precoce de Autismo',
        slug='home',
        locale=locale,
    )
    
    try:
        # Adicionar como filha da root
        root.add_child(instance=home_page)
        home_page.save_revision().publish()
        
        # Atualizar site root
        site.root_page = home_page
        site.save()
        
        print(f"✅ HomePage criada: {home_page.title}")
    except Exception as e:
        print(f"❌ Erro ao criar HomePage: {e}")
        # Tentar criar diretamente
        print("Tentando criar HomePage diretamente...")
        home_page = HomePage.objects.create(
            title='NeuroPrev - Triagem Precoce de Autismo',
            slug='home',
            locale=locale,
            depth=2,
            path=root.path + '0001',
        )
        home_page.save_revision().publish()
        site.root_page = home_page
        site.save()
        print(f"✅ HomePage criada diretamente: {home_page.title}")
else:
    print(f"✅ HomePage já existe: {home_page.title}")

print(f"✅ Site root: {site.root_page.title}")
print("\nAgora execute: python manage.py populate_site")
