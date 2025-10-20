from django.db import models
from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.html import escape

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock

from blocks.models import ListRedeSocial, ListRedesSociais


class PageSitePadrao(Page):
    """Classe base para todas as páginas do site."""
    
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
    """Classe base para páginas de índice do site."""
    class Meta:
        abstract = True


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    """Configurações gerais do site."""
    
    title_suffix = models.CharField(
        verbose_name="Título do Site",
        max_length=255,
        help_text="Título do site e utilizado como sufixo na tag meta. Ex.: ' | Site Padrão'",
        default="Site Padrão",
    )

    # --- Período Eleitoral ---
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
        default="Em respeito à legislação eleitoral (Lei 9.504/97), as notícias deste site/portal estão temporariamente suspensas."
    )

    # --- Redes Sociais e Compartilhamento ---
    redes_sociais = StreamField(
        [("lista_redes", ListRedeSocial())],
        verbose_name="Redes Sociais (Globais)",
        blank=True,
        use_json_field=True,
        help_text="Defina as redes sociais do Portal."
    )

    compartilhar_redes_sociais = models.BooleanField(
        verbose_name="Ativar Compartilhamento em Redes Sociais",
        default=False,
        help_text="Ative para exibir os botões de compartilhamento nas páginas."
    )

    compartilhar_rede_social = StreamField(
        [("redes_compartilhar", ListRedesSociais())],
        verbose_name="Selecionar Redes para Compartilhamento",
        blank=True,
        use_json_field=True,
        help_text="Escolha quais redes sociais estarão disponíveis para compartilhamento."
    )

    # --- Menu ---
    menu_max_levels = models.PositiveIntegerField(
        verbose_name="Níveis máximos do menu",
        default=1,
        help_text="Define até quantos níveis de páginas o menu principal irá exibir. (Máximo: 3)"
    )

    # --- Cookies e Analytics ---
    cookies_habilitado = models.BooleanField(
        verbose_name="Habilitar Aviso de Cookies",
        default=False,
        help_text="Ative para exibir o banner de consentimento de cookies no site."
    )
    google_analytics_tag = models.CharField(
        verbose_name="Tag do Google Analytics",
        max_length=20,
        blank=True,
        help_text="Insira a tag do Google Analytics (ex: G-XXXXXXXXXX)."
    )

    # --- Intranet ---
    intranet_habilitada = models.BooleanField(
        default=False,
        verbose_name="Ativar Intranet",
        help_text="Marque esta opção para ativar todas as funcionalidades da Intranet no site."
    )

    # --- Rodapé ---
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
                FieldPanel("compartilhar_redes_sociais"),
                FieldPanel("compartilhar_rede_social"),
            ],
            heading="Redes Sociais e Compartilhamento"
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
                FieldPanel("intranet_habilitada"),
            ],
            heading="Intranet"
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
    ]

    # --- Funções auxiliares ---
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

    def get_redes_ativas(self, absolute_url, page_title=None):
        """Gera a lista de redes sociais ativas com URLs de compartilhamento."""
        if not self.compartilhar_redes_sociais or not self.compartilhar_rede_social:
            return []

        redes_ativas = []
        for bloco in self.compartilhar_rede_social:
            for rede in bloco.value:
                dados = rede.value
                if dados.get("habilitado", False):
                    nome = dados.get("nome")
                    icone = dados.get("icone") or f"fa-brands fa-{nome}"
                    url = ""

                    if nome == "messenger":
                        url = f"https://www.facebook.com/dialog/send?link={absolute_url}&app_id=YOUR_APP_ID&redirect_uri={absolute_url}"
                    elif nome == "linkedin":
                        url = f"https://www.linkedin.com/shareArticle?mini=true&url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "pinterest":
                        url = f"https://pinterest.com/pin/create/button/?url={absolute_url}&description={escape(page_title or '')}"
                    elif nome == "x":
                        url = f"https://twitter.com/intent/tweet?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "reddit":
                        url = f"https://www.reddit.com/submit?url={absolute_url}&title={escape(page_title or '')}"
                    elif nome == "whatsapp":
                        url = f"https://api.whatsapp.com/send?text={escape(page_title or '')} {absolute_url}"
                    elif nome == "telegram":
                        url = f"https://t.me/share/url?url={absolute_url}&text={escape(page_title or '')}"
                    elif nome == "email":
                        url = f"mailto:?subject={escape(page_title or '')}&body={absolute_url}"
                    elif nome == "facebook":
                        url = f"https://www.facebook.com/sharer/sharer.php?u={absolute_url}"
                    elif nome == "sms":
                        url = f"sms:?body={escape(page_title or '')} {absolute_url}"
                    elif nome == "print":
                        url = "javascript:window.print();"
                    elif nome == "copy":
                        url = absolute_url

                    redes_ativas.append({
                        "nome": nome,
                        "icone": icone,
                        "url": url,
                    })

        return redes_ativas

    # --- Validações ---
    def clean(self):
        super().clean()

        if self.menu_max_levels > 3:
            raise ValidationError({
                "menu_max_levels": "O número máximo de níveis permitido para o menu é 3."
            })

        # Validação do Google Analytics
        if self.google_analytics_tag:
            tag = self.google_analytics_tag.strip()
            if tag and not (tag.startswith('G-') or tag.startswith('UA-') or tag.startswith('GT-')):
                raise ValidationError({
                    "google_analytics_tag": "A tag deve começar com 'G-', 'UA-' ou 'GT-' seguido do identificador."
                })

        if self.periodo_eleitoral_habilitado:
            if not self.periodo_eleitoral_inicio or not self.periodo_eleitoral_fim:
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
