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
class ContatosPage(RoutablePageMixin, PageSitePadraoIndex): # Mantém esta definição
    titulo = models.CharField(max_length=255, default="Contatos", verbose_name="Título da Página")
    
    # Campo para escolha do layout de duas colunas, só relevante se houver 2 colunas de conteúdo
    two_column_layout_choice = models.CharField(
        max_length=20,
        choices=[
            ('60_40', 'Duas Colunas (60/40)'),
        ],
        default='50_50',
        blank=True,
        null=True, # Permite que o campo seja nulo no banco de dados
        verbose_name="Escolha de Layout para Duas Colunas",
        help_text="Selecione o layout para as duas colunas de conteúdo. Será ignorado se a página tiver 1 ou 3 colunas."
    )

    body = StreamField(
        [
            ('coluna', ContatosColumnBlock()),
        ],
        use_json_field=True,
        blank=True, # Permite que o StreamField esteja vazio
        verbose_name="Conteúdo da Página" # Renomeado para ser mais genérico
    )

    tags = ClusterTaggableManager(through=ContatosPageTag, blank=True)

    parent_page_types = ["home.HomePage"] # Mantém o tipo de página pai
    subpage_types = []

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("two_column_layout_choice"), # Usa o novo campo
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

        layout_to_use = "no_blocks"

        if has_col1 and has_col2 and has_widget:
            layout_to_use = "40_40_20"
        elif has_col1 and has_col2:
            layout_to_use = self.two_column_layout_choice or '50_50'
        elif (has_col1 or has_col2) and has_widget:
            layout_to_use = self.two_column_layout_choice if self.two_column_layout_choice in ['70_30', '60_40'] else '70_30'
        elif has_col1:
            layout_to_use = "100_col1"
        elif has_col2:
            layout_to_use = "100_col2"
        elif has_widget:
            layout_to_use = "100_widget"

        return {
            "col1_blocks": col1_blocks,
            "col2_blocks": col2_blocks,
            "widget_blocks": widget_blocks,
            "layout": layout_to_use,
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

# Remove a definição duplicada da classe ContatosPage que estava aqui.
