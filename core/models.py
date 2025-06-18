from django.db import models
from datetime import date

from wagtail.contrib.settings.models import (
    BaseSiteSetting,
    register_setting,
)

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.fields import StreamField

from blocks.models import ListRedeSocial

# Create your models here.

@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    title_suffix = models.CharField(
        verbose_name="Titulo do Site",
        max_length=255,
        help_text="Titulo do site e utilizado como sufixo na tag meta. Ex.:' | Site Padrão'",
        default="Site Padrão",
    )

    periodo_eleitoral_habilitado = models.BooleanField(
        verbose_name="Habilitar Período Eleitoral",
        default=False,
        help_text="Ative para indicar que o site está em período eleitoral."
    )
    periodo_eleitoral_inicio = models.DateField(
        verbose_name="Data de início do período eleitoral",
        null=True,
        blank=True
    )
    periodo_eleitoral_fim = models.DateField(
        verbose_name="Data de fim do período eleitoral",
        null=True,
        blank=True
    )
    texto_informativo_periodo_eleitoral = models.TextField(
        verbose_name="Texto informativo do período eleitoral",
        blank=True,
        default="Em respeito a legislação eleitoral, Lei 9.504/97, as notícias deste site/portal está temporariamente suspensa."
    )

    redes_sociais = StreamField(
        [("lista_redes", ListRedeSocial())],
        verbose_name="Redes Sociais",
        blank=True,
        use_json_field=True,
    )

    panels = [
        FieldPanel("title_suffix"),
        MultiFieldPanel(
            [
                FieldPanel("periodo_eleitoral_habilitado"),
                FieldPanel("periodo_eleitoral_inicio"),
                FieldPanel("periodo_eleitoral_fim"),
                FieldPanel("texto_informativo_periodo_eleitoral"),
            ],
            heading="Período Eleitoral"
        ),
        MultiFieldPanel(
            [
                FieldPanel("redes_sociais"),
            ],
            heading="Redes Sociais"
        ),
    ]

    def is_periodo_eleitoral(self):
        """
        Retorna True se o período eleitoral está habilitado e a data atual está entre o início e o fim.
        """
        if not self.periodo_eleitoral_habilitado:
            return False
        hoje = date.today()
        if self.periodo_eleitoral_inicio and self.periodo_eleitoral_fim:
            return self.periodo_eleitoral_inicio <= hoje <= self.periodo_eleitoral_fim
        return False
