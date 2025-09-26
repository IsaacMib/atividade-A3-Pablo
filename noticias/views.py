from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.panels import FieldPanel

from .models import NoticiasPage

class NoticiasPageViewSet(ModelViewSet):
    model = NoticiasPage
    ordering = ("title",)
    list_display = ("title", "url", "destaque",)
    search_fields = ("title","destaque",)
    icon = "document"
    inspect_view_enabled = True
