from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail import hooks
from django.urls import reverse
from wagtail.admin.menu import MenuItem, Menu, SubmenuMenuItem
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from .models import CategoriaNoticias, NoticiasPage

@hooks.register('register_permissions')
def register_custom_permissions():
    noticia_ct = ContentType.objects.get(
        app_label='noticias', model='noticiaspage')
    return Permission.objects.filter(
        content_type=noticia_ct,
        codename='view_conteudo_migrado'
    )


@hooks.register('register_admin_menu_item')
def register_noticias_submenu():

    submenu = Menu(items=[
        MenuItem(
            'Categoria de Notícia',
            reverse('wagtailsnippets_noticias_categorianoticias:list'),
            icon_name='tag'
        ),
    ])
    return SubmenuMenuItem('Notícias', submenu, icon_name='doc-full-inverse', order=250)

register_snippet(CategoriaNoticias)


@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):

  menu_items[:] = [item for item in menu_items if item.name != 'snippets']
