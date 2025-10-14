from wagtail.blocks import (
    CharBlock,
    DateTimeBlock,
    StructBlock,
    StreamBlock,
    URLBlock,
)
from blocks.models import EspecificDocumentChooserBlock


class AnexoChoiceBlock(StreamBlock):
    arquivo = StructBlock([
        ('nome_documento', CharBlock(required=True, label="Nome para exibição do arquivo")),
        ('documento', EspecificDocumentChooserBlock(required=True, label="Arquivo")),
    ], label="Arquivo", icon="doc-full-inverse")

    link_externo = StructBlock([
        ('nome_link', CharBlock(required=True, label="Nome para exibição do link")),
        ('url', URLBlock(required=True, label="URL do link externo")),
    ], label="Link Externo", icon="link")

    class Meta:
        label = "Anexo"
        max_num = 1


class FaseEditalBlock(StructBlock):
    titulo_fase = CharBlock(required=True, label="Título da Fase")
    data_fase = DateTimeBlock(required=True, label="Data e Hora da Fase")
    anexo = AnexoChoiceBlock(required=False)

    class Meta:
        icon = 'date'
        label = "Fase do Edital"
        template = 'fase_edital_block.html'


SITUACAO_EDITAL_CHOICES = [
    ('aberto', 'Aberto'),
    ('em_andamento', 'Em Andamento'),
    ('encerrado', 'Encerrado'),
    ('suspenso', 'Suspenso'),
    ('cancelado', 'Cancelado'),
]