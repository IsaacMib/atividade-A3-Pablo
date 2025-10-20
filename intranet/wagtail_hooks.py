from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem
from django.urls import reverse_lazy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup
from core.models import SiteSettings
from .views import GrupoIntranetViewSet


class IntranetMenuGroup(SnippetViewSetGroup):
    menu_label = "Intranet"
    menu_icon = "cogs"
    menu_order = 300
    items = (GrupoIntranetViewSet,)

    def is_shown(self, request):
        settings = SiteSettings.for_request(request)
        return settings.intranet_habilitada

    def get_menu_item(self, order=None):

        menu_item = super().get_menu_item(order=order)
        menu_item.is_shown = self.is_shown
        return menu_item


register_snippet(IntranetMenuGroup)
