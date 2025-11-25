"""
Models para o app Contato - Formulário de contato e informações estruturadas.
"""

from django.db import models
from django.conf import settings
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib import messages

from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.admin.panels import FieldPanel, InlinePanel, TabbedInterface, ObjectList
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase


# === BLOCOS DE CONTATO (ESTRUTURA AVANÇADA) ===

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

    class Meta:
        icon = "doc-full"


class ContatoSimplesBlock(blocks.StructBlock):
    """Bloco para um contato direto, sem agrupamento."""
    titulo = blocks.CharBlock(required=False, label="Título (Ex: Presidência)")
    informacoes = blocks.ListBlock(ContatoInfoBlock(), label="Informações de Contato")
    mostrar_linha_separadora = blocks.BooleanBlock(
        required=False, 
        default=True, 
        label="Mostrar linha separadora após este grupo"
    )

    class Meta:
        label = "Contato Simples"
        icon = "user"


class ContatosSectionBlock(blocks.StructBlock):
    """Seção de contatos com título e estilo personalizável."""
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


# === TAGS ===
class ContatosPageTag(TaggedItemBase):
    """Tags para páginas de contato."""
    content_object = ParentalKey(
        "ContatoPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# === CAMPOS DO FORMULÁRIO ===
class FormField(AbstractFormField):
    """Campo customizado para o formulário de contato."""
    page = ParentalKey(
        'ContatoPage',
        on_delete=models.CASCADE,
        related_name='form_fields'
    )


# === PÁGINA DE CONTATO UNIFICADA ===
class ContatoPage(RoutablePageMixin, AbstractEmailForm):
    """
    Página de Contato com formulário e informações estruturadas.
    
    Combina:
    - Formulário de contato (AbstractEmailForm)
    - Informações estruturadas em colunas (StreamField)
    - Sistema de tags para categorização
    - Roteamento para arquivos por tag
    """
    
    parent_page_types = ['home.HomePage']
    subpage_types = []
    
    # === FORMULÁRIO ===
    intro = RichTextField(
        verbose_name="Texto Introdutório",
        blank=True,
        help_text="Texto exibido acima do formulário"
    )
    
    thank_you_text = RichTextField(
        verbose_name="Texto de Agradecimento",
        blank=True,
        help_text="Texto exibido após envio do formulário"
    )
    
    # === INFORMAÇÕES DE CONTATO SIMPLES ===
    email_contato = models.EmailField(
        verbose_name="Email de Contato",
        blank=True,
        help_text="Email institucional exibido na página"
    )
    
    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        blank=True
    )
    
    endereco = models.TextField(
        verbose_name="Endereço",
        blank=True
    )
    
    horario_atendimento = models.CharField(
        max_length=200,
        verbose_name="Horário de Atendimento",
        blank=True,
        help_text="Ex: Segunda a Sexta, 9h-17h"
    )
    
    # === INFORMAÇÕES ESTRUTURADAS (2 COLUNAS) ===
    coluna_1 = StreamField(
        [('contatos_section', ContatosSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 1 - Contatos Estruturados"
    )

    coluna_2 = StreamField(
        [('contatos_section', ContatosSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name="Coluna 2 - Contatos Estruturados"
    )
    
    # === TAGS ===
    tags = ClusterTaggableManager(through=ContatosPageTag, blank=True)
    
    # === CONTROLE DE ACESSO ===
    requires_login = models.BooleanField(
        default=False,
        verbose_name="Requer Login",
        help_text="Marque para exigir autenticação para visualizar a página"
    )
    
    # === PAINÉIS DO ADMIN ===
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Campos do Formulário"),
        FieldPanel('thank_you_text'),
        FieldPanel('email_contato'),
        FieldPanel('telefone'),
        FieldPanel('endereco'),
        FieldPanel('horario_atendimento'),
        FieldPanel('coluna_1'),
        FieldPanel('coluna_2'),
        FieldPanel('tags'),
        FormSubmissionsPanel(),
    ]
    
    settings_panels = AbstractEmailForm.settings_panels + [
        FieldPanel('requires_login'),
    ]
    
    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Conteúdo'),
        ObjectList(AbstractEmailForm.promote_panels, heading='Promover'),
        ObjectList(settings_panels, heading='Configurações', classname="settings"),
    ])
    
    # === MÉTODOS ===
    def serve(self, request, *args, **kwargs):
        """Serve a página com controle de acesso."""
        if self.requires_login and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={self.url}")
        return super().serve(request, *args, **kwargs)
    
    def get_context(self, request):
        """Adiciona ícones aos tipos de contato no contexto."""
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

        context["coluna_1"] = self.coluna_1
        context["coluna_2"] = self.coluna_2

        return context

    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """Rota para filtrar contatos por tag."""
        try:
            tag_obj = Tag.objects.get(slug=slugify(tag))
        except Tag.DoesNotExist:
            if tag:
                messages.info(request, f'Não há contatos com a tag "{tag}"')
            return redirect(self.url)

        contatos = ContatoPage.objects.live().filter(tags=tag_obj)
        context = self.get_context(request)
        context.update({
            "tag": tag_obj,
            "contatos": contatos,
        })
        return render(request, "contato/contato_page.html", context)
    
    class Meta:
        verbose_name = "Página de Contato"
        verbose_name_plural = "Páginas de Contato"
