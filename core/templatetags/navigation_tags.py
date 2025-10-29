from django import template
from wagtail.models import Site
from core.models import SiteSettings  # Import necessário
from django.conf import settings

register = template.Library()
# https://docs.djangoproject.com/en/stable/howto/custom-template-tags/


@register.simple_tag(takes_context=True)
def get_site_root(context):
    # This returns a core.Page. The main menu needs to have the site.root_page
    # defined else will return an object attribute error ('str' object has no
    # attribute 'get_children')
    return Site.find_for_request(context["request"]).root_page


def has_children(page):
    # Generically allow index pages to list their children
    return page.get_children().live().exists()


def is_active(page, current_page):
    # To give us active state on main navigation
    return current_page.url_path.startswith(page.url_path) if current_page else False


def get_menuitems_with_children(page, calling_page, max_levels, current_level=1, start_index=1):
    menuitems = page.get_children().live().in_menu().order_by('title')
    items = []
    index = start_index
    for menuitem in menuitems:
        # Verifica se calling_page é uma página válida antes de acessar url_path
        if calling_page and hasattr(calling_page, 'url_path') and hasattr(menuitem, 'url_path'):
            menuitem.active = calling_page.url_path.startswith(menuitem.url_path)
        else:
            menuitem.active = False
            
        # Só atribui index se for nível 2
        if current_level == 2:
            menuitem.index = index
            index += 1
        if max_levels is None or current_level < max_levels:
            children, next_index = get_menuitems_with_children(
                menuitem, calling_page, max_levels, current_level + 1, index
            )
            menuitem.children = children
            # Só atualiza index para o próximo irmão de nível 2
            if current_level == 2:
                index = next_index
        else:
            menuitem.children = []
        items.append(menuitem)
    return items, index


# Retrieves the top menu items - the immediate children of the parent page
@register.inclusion_tag("tags/top_menu.html", takes_context=True)
def top_menu(context, parent, calling_page=None, max_levels=None):
    """
    Retorna os itens do menu até max_levels níveis, usando SiteSettings se não informado.
    """
    if max_levels is None:
        site = Site.find_for_request(context["request"])
        site_settings = SiteSettings.for_site(site)
        max_levels = site_settings.menu_max_levels

    menuitems, _ = get_menuitems_with_children(parent, calling_page, max_levels)
    return {
        "calling_page": calling_page,
        "menuitems": menuitems,
        # required by the pageurl tag that we want to use within this template
        "request": context["request"],
        "max_levels": max_levels,
        "HABILITAR_SITE_INTRANET": context.get("HABILITAR_SITE_INTRANET", False),
    }

