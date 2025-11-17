from django.db import models
from core.models import PageSitePadrao
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from paginas.models import PaginaComBannerPage

class LGPDPage(PaginaComBannerPage):
    template = "paginas/pagina_com_banner_page.html"

    class Meta:
        verbose_name = "LGPD"
        verbose_name_plural = "LGPD"



