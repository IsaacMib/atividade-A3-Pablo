from django.db import models

from wagtail.contrib.settings.models import (
    BaseSiteSetting,
    register_setting,
)

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)

# Create your models here.

@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name="Titulo do Site",
        max_length=255,
        help_text="Titulo do site e utilizado como sufixo na tag meta. Ex.:' | Site Padrão'",
        default="Site Padrão",
    ) 

    panels = [
        FieldPanel("title_suffix"),
    ]
