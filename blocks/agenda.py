from wagtail.blocks import (
    CharBlock,
    StructBlock,
    DateBlock,
    TimeBlock,
    TextBlock,
    ListBlock,
    PageChooserBlock,
)

from django.core.exceptions import ValidationError


class ListAgendaBlock(StructBlock):
    agenda_page = PageChooserBlock(
        target_model="agenda.AgendaPage",
        required=True,
        label="Selecione a página da agenda"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        agenda_page = value.get('agenda_page')
        context['agenda_page_title'] = agenda_page.title if agenda_page else ""
        context['agenda_page_url'] = agenda_page.url if agenda_page else ""
        context['agenda_page_id'] = agenda_page.id if agenda_page else None
        return context

    class Meta:
        icon = 'list-ul'
        label = "Listar Agenda"
        template = 'blocks/list_agenda.html'


class CompromissoBlock(StructBlock):
    """
    Bloco para representar um compromisso na agenda.
    """
    title = CharBlock(required=True, max_length=255, label="Título do compromisso")
    nome_autoridade = CharBlock(required=False, max_length=255, label="Nome da autoridade")
    inicio = TimeBlock(required=True, label="Hora início")
    termino = TimeBlock(required=True, label="Hora término")
    outros_participantes = TextBlock(required=False, label="Outros Participantes")
    pauta = TextBlock(required=False, label="Pauta")
    local = CharBlock(required=False, max_length=255, label="Local do compromisso")

    def clean(self, value):
        cleaned_data = super().clean(value)
        inicio = cleaned_data.get("inicio")
        termino = cleaned_data.get("termino")
        if inicio and termino and inicio > termino:        
            raise ValidationError({
                    "inicio": "A hora de início não pode ser maior que a hora de término.",
                })
        if termino and inicio and termino < inicio:
            raise ValidationError({
                    "termino": "A hora de término não pode ser menor que a hora de início.",
                })
        return cleaned_data

    class Meta:
        icon = "time"
        label = "Compromisso"
        template = "blocks/compromisso_block.html"
        form_classname = "struct-block collapsed"  # Adicionado para colapsar


class AgendaDoDiaBlock(StructBlock):
    """
    Bloco para representar a agenda de um dia, contendo múltiplos compromissos.
    """
    date = DateBlock(required=True, label="Data da Agenda")
    compromissos = ListBlock(
        CompromissoBlock(),
        label="Compromissos do Dia",
        sortable=True,
        collapsed=True,  # Adicionado para colapsar os itens da lista
    )

    class Meta:
        icon = "date"
        label = "Agenda do Dia"
        template = "blocks/agenda_do_dia_block.html"
        form_classname = "struct-block collapsed"  # Adicionado para colapsar