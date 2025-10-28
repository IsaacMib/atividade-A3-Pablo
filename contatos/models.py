from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

from core.models import PageSitePadraoIndex


# === BLOCOS DE CONTATO (NOVA ESTRUTURA) ===

class ContatoInfoBlock(blocks.StructBlock):
    """Bloco para uma informação de contato individual (ex: um telefone, um email)."""

    TIPO_CHOICES = [
        ('phone', 'Telefone'),
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('text', 'Outro (Texto)'),
    ]
    tipo = blocks.ChoiceBlock(choices=TIPO_CHOICES, default='phone', label="Tipo de Contato")
    info = blocks.CharBlock(required=True, label="Informação")

    def clean(self, value):
        """Valida e formata o campo de telefone automaticamente."""
        cleaned_data = super().clean(value)
        tipo = cleaned_data.get('tipo')
        info = cleaned_data.get('info', '').strip()

        # Normaliza e formata telefone
        if tipo in ('phone', 'whatsapp'):
            import re

            digits = re.sub(r'\D', '', info)
            # Validação de formato (DDD + número)
            if not re.match(r'^[1-9]{2}\d{8,9}$', digits):
                raise ValidationError({'info': "DDD inválido ou formato incorreto. Use DDD + número (10 ou 11 dígitos)."})

            ddd = digits[:2]
            if len(digits) == 10:
                num = f"{digits[2:6]}-{digits[6:]}"
            else:
                num = f"{digits[2:7]}-{digits[7:]}"
            cleaned_data['info'] = f"({ddd}) {num}"

        elif tipo == 'email':
            from django.core.validators import validate_email
            try:
                validate_email(info)
            except ValidationError:
                raise ValidationError({'info': "E-mail inválido."})

        return cleaned_data


class ContatoIndividualBlock(blocks.StructBlock):
    """Bloco para um contato específico, que pode ter múltiplas informações."""
    titulo = blocks.CharBlock(required=False, label="Nome do Contato ou Setor")
    informacoes = blocks.ListBlock(ContatoInfoBlock(), label="Informações de Contato")

    class Meta:
        label = "Contato"


class ContatoSimplesBlock(blocks.StructBlock):
    """Bloco para um contato direto, sem agrupamento."""
    titulo = blocks.CharBlock(required=False, label="Título (Ex: Presidência)")
    informacoes = blocks.ListBlock(ContatoInfoBlock(), label="Informações de Contato")
    mostrar_linha_separadora = blocks.BooleanBlock(required=False, default=True, label="Mostrar linha separadora após este grupo")

    class Meta:
        label = "Contato Simples"
        icon = "user"

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
            ('triangle', 'Triângulo ►'),
            ('chevron', 'Ponta de Flecha ›'),
            ('black_diamond', 'Diamante Negro ◆'),
        ],
        default='dot',
        label="Estilo da lista da seção",
    )

    itens_contato = blocks.StreamBlock([
        ('contato_simples', ContatoSimplesBlock()),
    ], use_json_field=True, label="Itens de Contato")

    class Meta:
        icon = "list-ul"
        label = "Seção de Contatos"


CONTENT_BLOCKS = [
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

    tags = ClusterTaggableManager(through=ContatosPageTag, blank=True)

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = PageSitePadraoIndex.content_panels + [
        FieldPanel("coluna_1"),
        FieldPanel("coluna_2"),
        FieldPanel("tags"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(PageSitePadraoIndex.promote_panels, heading='Promover'),
        ObjectList(PageSitePadraoIndex.settings_panels, heading='Configurações', classname="settings"),
    ])

    requires_login = True  # pode desativar isso se quiser liberar a página

    def serve(self, request, *args, **kwargs):
        if getattr(self, "requires_login", False) and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={self.url}")
        return super().serve(request, *args, **kwargs)
    
    def get_context(self, request):
        context = super().get_context(request)

        colunas = [self.coluna_1, self.coluna_2]

        for coluna in colunas:
            if not coluna:
                continue

            for bloco in coluna:
                if bloco.block_type != "contatos_section":
                    continue

                section_value = bloco.value
                itens = section_value.get("itens_contato", [])

                for item in itens:
                    contato = item.value
                    informacoes = contato.get("informacoes", [])

                    for info in informacoes:
                        tipo = info.get("tipo") if isinstance(info, dict) else getattr(info, "tipo", None)
                        icone = {
                            "phone": '<i class="bi bi-telephone"></i>',
                            "email": '<i class="bi bi-envelope"></i>',
                            "whatsapp": '<i class="bi bi-whatsapp"></i>',
                            "text": '<i class="bi bi-card-text"></i>',
                        }.get(tipo, "")

                        if isinstance(info, dict):
                            info["icone"] = icone
                        else:
                            setattr(info, "icone", icone)

        return context


    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        try:
            tag_obj = Tag.objects.get(slug=slugify(tag))
        except Tag.DoesNotExist:
            if tag:
                messages.info(request, f'Não há contatos com a tag "{tag}"')
            return redirect(self.url)

        contatos = ContatosPage.objects.live().filter(tags=tag_obj)
        context = self.get_context(request)
        context.update({
            "tag": tag_obj,
            "contatos": contatos,
        })
        return render(request, "contatos/contatos_page.html", context)
