from datetime import date
from django.db import models

from django.core.exceptions import ValidationError
from django.utils.html import escape
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from blocks.models import ListRedeSocial


class PageSitePadrao(Page):

    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        help_text="Descrição da página para SEO e redes sociais"
    )

    imagem_destaque = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem de Destaque",
        help_text="Imagem usada em destaque para SEO e redes sociais"
    )

    content_panels = Page.content_panels + [
        FieldPanel("descricao"),
        
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("imagem_destaque"),
    ]

    def get_imagem_destaque(self):
        """
        Retorna a imagem de destaque da página ou None se não houver.
        """
        return self.imagem_destaque

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
    """
    Configurações do site acessíveis via Wagtail Settings.
    Adiciona campos de título, período eleitoral, redes sociais, menu,
    cookies / analytics e reCAPTCHA (site + secret).
    """

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
        help_text="Defina as redes sociais do Portal."
    )

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

    footer_titulo_instituicao = models.CharField(
       max_length=255,
       blank=True,
       verbose_name="Título da Instituição no Rodapé",
       default="CENTRO ADMINISTRATIVO ESTADUAL"
    )
    footer_informacoes = models.TextField(
        blank=True,
        verbose_name="Informações do Rodapé",
        help_text="Endereço, telefone, horário, CNPJ. Use <br> para quebras de linha.",
        default="Rua João da Mata, S/N, Jaguaribe - CEP: 58.015-020<br>\nFone: Recepção: (83) 98658-8328 - JOÃO PESSOA - PARAÍBA<br>\nHorário de Atendimento: Das 8:00 às 16:30<br>\nCNPJ: 09.189.499/0001-00"
    )
    footer_link_sic = models.URLField(
        blank=True,
        verbose_name="Link para o SIC (Serviço de Informação ao Cidadão)",
        default="https://sic.pb.gov.br/"
    )
    footer_imagem_sic = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem do SIC no rodapé",
        help_text="Faça o upload da imagem do logo do SIC."
    )

    captcha_site_key = models.CharField(
        verbose_name="Captcha Site Key (pública)",
        max_length=255,
        blank=True,
        help_text="Chave pública (site key) do reCAPTCHA usada no cliente (frontend)."
    )


    captcha_secret_key = models.CharField(
        verbose_name="Captcha Secret Key (secreta)",
        max_length=255,
        blank=True,
        help_text="Chave secreta do reCAPTCHA usada para validação no servidor. (Deixe em branco se não usar captcha)"
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
        MultiFieldPanel(
            [
                FieldPanel("footer_titulo_instituicao"),
                FieldPanel("footer_informacoes"),
                FieldPanel("footer_link_sic"),
                FieldPanel("footer_imagem_sic"),
            ],
            heading="Rodapé",
            classname="collapsible collapsed"
        ),
        MultiFieldPanel(
            [
                FieldPanel("captcha_site_key"),
                FieldPanel("captcha_secret_key"),
            ],
            heading="Captcha (reCAPTCHA)"
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
        """Retorna True se o aviso de cookies deve ser exibido."""
        return self.cookies_habilitado

    def tem_google_analytics(self):
        """Retorna True se a tag do Google Analytics está configurada."""
        return bool(self.google_analytics_tag and self.google_analytics_tag.strip())

    def deve_exibir_cookies_analytics(self):
        """
        Retorna True se o aviso de cookies analíticos deve ser exibido.
        Só exibe se os cookies estão habilitados E a tag do Google Analytics está definida.
        """
        return self.deve_exibir_cookies() and self.tem_google_analytics()
    
    def tem_captcha_site(self):
        return bool(self.captcha_site_key and self.captcha_site_key.strip())


    def tem_captcha_secret(self):
        return bool(self.captcha_secret_key and self.captcha_secret_key.strip())


    def has_recaptcha_keys(self):
        return self.tem_captcha_site() and self.tem_captcha_secret()


    def get_captcha_site_key(self):
        return self.captcha_site_key.strip() if self.tem_captcha_site() else None


    def get_captcha_secret(self):
        return self.captcha_secret_key.strip() if self.tem_captcha_secret() else None


    def tem_captcha_site(self):
        return bool(self.captcha_site_key and self.captcha_site_key.strip())

    def tem_captcha_secret(self):
        return bool(self.captcha_secret_key and self.captcha_secret_key.strip())

    def has_recaptcha_keys(self):
        return self.tem_captcha_site() and self.tem_captcha_secret()

    def get_captcha_site_key(self):
        return self.captcha_site_key.strip() if self.tem_captcha_site() else None

    def get_captcha_secret(self):
        return self.captcha_secret_key.strip() if self.tem_captcha_secret() else None

    def clean(self):
        super().clean()

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
            if self.captcha_site_key:
                site = self.captcha_site_key.strip()
                if site and len(site) < 10:
                    raise ValidationError({
                        "captcha_site_key": "A site key do captcha parece ser muito curta."
                })
            if self.captcha_secret_key:
                secret = self.captcha_secret_key.strip()
                if secret and len(secret) < 10:
                    raise ValidationError({
                        "captcha_secret_key": "A chave secreta do captcha parece ser muito curta."
               })
