from django.db import models
from core.models import PageSitePadrao
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks

# Alterado: herdar de PageSitePadrao em vez de PaginaComBannerPage (app deletado)
class LGPDPage(PageSitePadrao):
    template = "lgpd/lgpd_page.html"

    class Meta:
        verbose_name = "LGPD"
        verbose_name_plural = "LGPD"



