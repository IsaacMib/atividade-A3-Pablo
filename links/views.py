
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.panels import FieldPanel

from .models import LinkCabecalhoItemBlock

class LinkCabecalhoViewSet(ModelViewSet):
    model = LinkCabecalhoItemBlock
    ordering = ("titulo",)
    list_display = ("titulo", "url", "target",)
    search_fields = ("titulo",)
    icon = "link"
    inspect_view_enabled = True
