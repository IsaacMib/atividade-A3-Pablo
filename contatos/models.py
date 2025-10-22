from django.db import models
from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from django.core.validators import RegexValidator 
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail import blocks
from core.models import PageSitePadraoIndex
from wagtail.admin.panels import TabbedInterface, ObjectList
from django.core.exceptions import ValidationError


# === BLOCOS DE CONTATO (NOVA ESTRUTURA) ===

class ContatoInfoBlock(blocks.StructBlock):
    """Bloco para uma informação de contato individual (ex: um telefone, um email)."""
    phone_validator = RegexValidator(
        regex=r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$',
        message="Use um formato de telefone válido, ex: (83) 3208-4451."
    )
    TIPO_CHOICES = [
        ('phone', 'Telefone'),
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('text', 'Outro (Texto)'),
    ]
    tipo = blocks.ChoiceBlock(choices=TIPO_CHOICES, default='phone', label="Tipo de Contato")
    info = blocks.CharBlock(required=True, label="Informação")

    class Meta:
        label = "Informação de Contato"


class ContatoIndividualBlock(blocks.StructBlock):
    """Bloco para um contato específico, que pode ter múltiplas informações."""
    titulo = blocks.CharBlock(required=False, label="Nome do Contato ou Setor")
    informacoes = blocks.ListBlock(ContatoInfoBlock(), label="Informações de Contato")

    class Meta:
        label = "Contato"


class ContatoSimplesBlock(blocks.StructBlock):
    """Bloco para um contato direto, sem agrupamento."""
    titulo = blocks.CharBlock(required=False, label="Título (Ex: Presidência)")
    list_style = blocks.ChoiceBlock(
        choices=[
            ('none', 'Sem marcador'),
            ('dot', 'Ponto •'),
            ('diamond', 'Diamante ♦'),
            ('arrow', 'Seta ➤'),
            ('triangle', 'Triângulo ▲'),
            ('chevron', 'Ponta de Flecha ›'),
            ('black_diamond', 'Diamante Negro ◆'),
        ],
        default='none',
        label="Estilo da lista de contatos",
    )
    informacoes = blocks.ListBlock(ContatoInfoBlock(), label="Informações de Contato")
    mostrar_linha_separadora = blocks.BooleanBlock(required=False, default=True, label="Mostrar linha separadora após este grupo")

    class Meta:
        label = "Contato Simples"
        icon = "user"


class GrupoContatosBlock(blocks.StructBlock):
    """Bloco para um grupo de contatos, ex: 'Assessorias'."""
    titulo_grupo = blocks.CharBlock(required=True, label="Título do Grupo (Ex: Assessorias)")
    mostrar_linha_separadora = blocks.BooleanBlock(required=False, default=True, label="Mostrar linha separadora após este grupo")
    contatos = blocks.ListBlock(ContatoIndividualBlock())

    class Meta:
        label = "Grupo de Contatos"
        icon = "group"

    list_style = blocks.ChoiceBlock(
        choices=[
            ('none', 'Sem marcador'),
            ('dot', 'Ponto •'),
            ('diamond', 'Diamante ♦'),
            ('arrow', 'Seta ➤'),
            ('triangle', 'Triângulo ▲'),
            ('chevron', 'Ponta de Flecha'),
            ('black_diamond', 'Diamante Negro ◆'),
        ],
        default='dot',
        label="Estilo da lista de contatos",
    )


# === BLOCO DE SEÇÃO DE CONTATOS ===
class ContatosSectionBlock(blocks.StructBlock):
    section_title = blocks.CharBlock(required=True, label="Título da Seção")
    title_size = blocks.ChoiceBlock(
        choices=[
            ('small', 'Pequeno'),
            ('medium', 'Médio'),
            ('large', 'Grande'),
        ],
        default='medium',
        label="Tamanho do Título",
    )

    itens_contato = blocks.StreamBlock([
        ('contato_simples', ContatoSimplesBlock()),
        ('grupo_contatos', GrupoContatosBlock()),
    ], use_json_field=True, label="Itens de Contato")


    class Meta:
        icon = "list-ul"
        label = "Seção de Contatos"


CONTENT_BLOCKS = [
    ('contatos_section', ContatosSectionBlock()),
]

WIDGET_BLOCKS = [
    ('contatos_section', ContatosSectionBlock()),
]


# === TAGS ===
class ContatosPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ContatosPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# === PÁGINA PRINCIPAL ===
class ContatosPage(RoutablePageMixin, PageSitePadraoIndex):
    titulo = models.CharField(max_length=255, default="Contatos", verbose_name="Título da Página")

    LAYOUT_CHOICES = [
        ('100_col1', 'Layout: 100% (Coluna 1)'),
        ('100_col2', 'Layout: 100% (Coluna 2)'),
        ('100_widget', 'Layout: 100% (Widgets)'),
        ('50_50', 'Layout: 50% / 50%'),
        ('60_40', 'Layout: 60% / 40% (Conteúdo / Widgets)'),
        ('70_30', 'Layout: 70% / 30% (Conteúdo / Widgets)'),
        ('40_40_20', 'Layout: 40% / 40% / 20%'),
    ]

    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='100_col1',
        verbose_name="Layout da Página",
        help_text="Escolha a proporção e o conteúdo das colunas."
    )

    coluna_1 = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 1"
    )

    coluna_2 = StreamField(
        CONTENT_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 2"
    )

    widgets = StreamField(
        WIDGET_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Widgets (Coluna Lateral)"
    )

    tags = ClusterTaggableManager(through=ContatosPageTag, blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("coluna_1"),
        FieldPanel("coluna_2"),
        FieldPanel("widgets"),
        FieldPanel("tags"),
    ]

    layout_panels = [
        FieldPanel('layout'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(layout_panels, heading='Layout'),
        ObjectList(PageSitePadraoIndex.promote_panels, heading='Promover'),
        ObjectList(PageSitePadraoIndex.settings_panels, heading='Configurações', classname="settings"),
    ])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({
            "layout": self.layout,
            "col1_blocks": self.coluna_1,
            "col2_blocks": self.coluna_2,
            "widget_blocks": self.widgets,
        })
        return context

    def serve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{settings.LOGIN_URL}?next={self.get_url(request)}"
            return HttpResponseRedirect(login_url)
        return super().serve(request, *args, **kwargs)

    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        try:
            tag_obj = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                messages.info(request, f'Não há contatos com a tag "{tag}"')
            return redirect(self.url)

        # Esta parte pode precisar de ajuste dependendo do que você quer mostrar na página de tag
        # Atualmente, ela renderiza a própria página de contatos com um contexto adicional.
        # Se a intenção é listar outras páginas, a lógica precisa mudar.
        posts = ContatosPage.objects.live().filter(tags=tag_obj)
        context = self.get_context(request)
        context.update({"tag": tag_obj, "posts": posts})
        return render(request, "contatos/contatos_page.html", context)
