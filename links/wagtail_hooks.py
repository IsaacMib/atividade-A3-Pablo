from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .views import (
    LinkCabecalhoViewSet,
)

class LinksMenuGroup(SnippetViewSetGroup):
    menu_label = "Links"
    menu_icon = "link"
    menu_order = 200
    items = (
        LinkCabecalhoViewSet,
    )

register_snippet(LinksMenuGroup)


