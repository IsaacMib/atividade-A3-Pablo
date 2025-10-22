from django.db import models
from django import forms
from datetime import date
from django.core.exceptions import ValidationError

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock

from blocks.models import ListRedeSocial


from django.db import models
from datetime import date
from django.core.exceptions import ValidationError

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField

from blocks.models import ListRedeSocial


class PageSitePadrao(Page):
    """
    Classe base para todas as páginas do site.
    Herda de Page do Wagtail e adiciona campos comuns a todas as páginas.
    """
    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Descrição da página para SEO e redes sociais"
    )
    
    images = StreamField(
        [("image", ImageChooserBlock(label="Imagem"))],
        verbose_name="Imagens",
        blank=True,
        use_json_field=True,
        help_text="Imagens relacionadas à página"
    )

    content_panels = Page.content_panels + [
        FieldPanel("descricao"),
        FieldPanel("images"),
    ]

    class Meta:
        abstract = True


class PageSitePadraoIndex(Page):
    """
    Classe base para páginas de índice do site.
    Herda apenas de Page do Wagtail sem campos adicionais.
    """
    
    class Meta:
        abstract = True


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
        default="Em respeito a legislação eleitoral, Lei 9.504/97, as notícias deste site/portal estão temporariamente suspensa."
    )

    redes_sociais = StreamField(
        [("lista_redes", ListRedeSocial())],
        verbose_name="Redes Sociais",
        blank=True,
        use_json_field=True,
    )

    # Novo campo para controlar o nível máximo do menu
    menu_max_levels = models.PositiveIntegerField(
        verbose_name="Níveis máximos do menu",
        default=1,
        help_text="Define até quantos níveis de páginas o menu principal irá exibir. (Máximo: 3)"
    )

    # Configurações para cookies e Google Analytics
    cookies_habilitado = models.BooleanField(
        verbose_name="Habilitar Aviso de Cookies",
        default=False,
        help_text="Ative para exibir o banner de consentimento de cookies no site."
    )
    google_analytics_tag = models.CharField(
        verbose_name="Tag do Google Analytics",
        max_length=20,
        blank=True,
        help_text="Insira a tag do Google Analytics (ex: G-XXXXXXXXXX). O aviso de cookies analíticos só será exibido se esta tag estiver definida."
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
        MultiFieldPanel(
            [
                FieldPanel("menu_max_levels"),
            ],
            heading="Menu do Site"
        ),
        MultiFieldPanel(
            [
                FieldPanel("cookies_habilitado"),
                FieldPanel("google_analytics_tag"),
            ],
            heading="Cookies e Analytics"
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

    def deve_exibir_cookies(self):
        """
        Retorna True se o aviso de cookies deve ser exibido.
        """
        return self.cookies_habilitado

    def tem_google_analytics(self):
        """
        Retorna True se a tag do Google Analytics está configurada.
        """
        return bool(self.google_analytics_tag and self.google_analytics_tag.strip())

    def deve_exibir_cookies_analytics(self):
        """
        Retorna True se o aviso de cookies analíticos deve ser exibido.
        Só exibe se os cookies estão habilitados E a tag do Google Analytics está definida.
        """
        return self.deve_exibir_cookies() and self.tem_google_analytics()

    def clean(self):
        super().clean()
        if self.periodo_eleitoral_habilitado:
            if not self.periodo_eleitoral_inicio and not self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "Obrigatório quando o período eleitoral está habilitado.",
                    "periodo_eleitoral_fim": "Obrigatório quando o período eleitoral está habilitado.",
                })
            if not self.periodo_eleitoral_inicio:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "Obrigatório quando o período eleitoral está habilitado."
                })
            if not self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_fim": "Obrigatório quando o período eleitoral está habilitado."
                })
            if self.periodo_eleitoral_inicio > self.periodo_eleitoral_fim:
                raise ValidationError({
                    "periodo_eleitoral_inicio": "A data de início não pode ser posterior à data de fim.",
                    "periodo_eleitoral_fim": "A data de fim não pode ser anterior à data de início."
                })

        if self.menu_max_levels > 3:
            raise ValidationError({
                "menu_max_levels": "O número máximo de níveis permitido para o menu é 3."
            })

        if self.google_analytics_tag:
            tag = self.google_analytics_tag.strip()
            if tag and not (tag.startswith('G-') or tag.startswith('UA-') or tag.startswith('GT-')):
                raise ValidationError({
                    "google_analytics_tag": "A tag deve começar com 'G-', 'UA-' ou 'GT-' seguido do identificador."
                })


@register_setting(icon="link")
class ApiSettings(BaseSiteSetting):
    api_habilitada = models.BooleanField(
        verbose_name="Habilitar Integração via API",
        default=False,
        help_text="Marque esta opção para ativar a busca de conteúdo de um portal externo."
    )
    api_url = models.URLField(
        verbose_name="URL da API Externa",
        blank=True,
        help_text="URL base da API do portal de conteúdo externo."
    )
    api_usuario = models.CharField(
        max_length=255,
        verbose_name="Usuário da API",
        blank=True,
        help_text="Usuário para autenticação na API externa."
    )
    api_senha = models.CharField(
        max_length=255,
        verbose_name="Senha da API",
        blank=True,
        help_text="Senha para autenticação na API externa. Cuidado: será armazenada como texto plano."
    )

    puxar_noticias = models.BooleanField(
        verbose_name="Puxar Notícias",
        default=False,
        help_text="Ativar para buscar notícias do portal externo."
    )
    tags_noticias = models.CharField(
        max_length=255,
        verbose_name="Tags de Notícias",
        blank=True,
        help_text="Separar tags por vírgula. Ex: 'geral, importante'. Deixe em branco para buscar todas."
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("api_habilitada"),
                FieldPanel("api_url"),
                FieldPanel("api_usuario"),
                FieldPanel("api_senha"),
            ],
            heading="Integração de Conteúdo Externo"
        ),
        MultiFieldPanel(
            [
                FieldPanel("puxar_noticias"),
                FieldPanel("tags_noticias"),
            ],
            heading="Tipos de Conteúdo para que será consumido",
            classname="collapsible collapsed"
        ),
    ]
    class Meta:
        verbose_name = "Configurações de Conteúdo Externo"
