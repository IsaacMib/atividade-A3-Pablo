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
from django.core.exceptions import ValidationError


# === BLOCO DE ITENS DE CONTATO ===
class ContatosItemBlock(blocks.StructBlock):
    phone_validator = RegexValidator(
        regex=r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$',
        message="Use um formato de telefone válido, ex: (83) 3208-4451."
    )
    title = blocks.CharBlock(required=False, label="Nome ou Setor")
    phone = blocks.CharBlock(required=True, label="Telefone", validators=[phone_validator])


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

    contatos = blocks.ListBlock(ContatosItemBlock())

    class Meta:
        icon = "list-ul"
        label = "Seção de Contatos"


# === BLOCO DE COLUNA (estrutura principal) ===
class ContatosColumnBlock(blocks.StructBlock):
    coluna = blocks.ChoiceBlock(
        choices=[
            ('coluna_1', 'Primeira Coluna'),
            ('coluna_2', 'Segunda Coluna'),
            ('coluna_3', 'Widgets'),
        ],
        default='coluna_1',
        label="Posição do bloco na página"
    )

    conteudo = blocks.StreamBlock(
        [
            ('contatos_section', ContatosSectionBlock()),
        ],
        required=True,
        label="Conteúdo do bloco"
    )


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

    body = StreamField(
        [
            ('coluna', ContatosColumnBlock()),
        ],
        use_json_field=True,
        blank=True,
        verbose_name="Conteúdo da Página"
    )

    tags = ClusterTaggableManager(through=ContatosPageTag, blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("body"),
        FieldPanel("tags"),
    ]

    def get_layout_context(self):
        col1_blocks, col2_blocks, widget_blocks = [], [], []

        for block in self.body:
            if block.block_type == 'coluna' and block.value.get('conteudo'):
                coluna = block.value.get('coluna')
                if coluna == 'coluna_1':
                    col1_blocks.append(block)
                elif coluna == 'coluna_2':
                    col2_blocks.append(block)
                elif coluna == 'coluna_3':
                    widget_blocks.append(block)

        has_col1 = bool(col1_blocks)
        has_col2 = bool(col2_blocks)
        has_widget = bool(widget_blocks)

        if has_col1 and has_col2 and has_widget:
            layout = "40_40_20"
        elif has_col1 and has_col2:
            layout = "50_50"
        elif (has_col1 or has_col2) and has_widget:
            layout = "70_30"
        elif has_col1:
            layout = "100_col1"
        elif has_col2:
            layout = "100_col2"
        elif has_widget:
            layout = "100_widget"
        else:
            layout = "100_default"

        return {
            "col1_blocks": col1_blocks,
            "col2_blocks": col2_blocks,
            "widget_blocks": widget_blocks,
            "layout": layout,
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(self.get_layout_context())
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

        posts = ContatosPage.objects.live().filter(tags=tag_obj)
        context = self.get_context(request)
        context.update({"tag": tag_obj, "posts": posts})
        return render(request, "contatos/contatos_page.html", context)
