from django import forms
from wagtail.blocks import (
    StructBlock,
    CharBlock,
    EmailBlock,
    ChoiceBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    ListBlock,
    FloatBlock,
    PageChooserBlock,
    URLBlock,
    IntegerBlock,
    BooleanBlock
)
from .utils import validate_file_size

#CAMPOS DE FORMULÁRIO

class BaseFieldBlock(StructBlock):
    label = CharBlock(label="Rótulo do Campo")
    help_text = CharBlock(required=False, label="Texto de Ajuda")
    required = BooleanBlock(required=False, label="Campo Obrigatório?")

    class Meta:
        abstract = True
        icon = "form"
class SingleLineFieldBlock(BaseFieldBlock):
    class Meta:
        label = "Campo de Texto (linha única)"

class MultiLineFieldBlock(BaseFieldBlock):
    class Meta:
        label = "Campo de Texto (múltiplas linhas)"

class EmailFieldBlock(BaseFieldBlock):
    class Meta:
        label = "Campo de Email"

class NumberFieldBlock(BaseFieldBlock):
    class Meta:
        label = "Campo de Número"


class DropdownFieldBlock(BaseFieldBlock):
    choices = TextBlock(label="Opções", help_text="Liste uma opção por linha.")

    class Meta:
        label = "Menu de Opções"

class FileFieldBlock(BaseFieldBlock):
    class Meta:
        label = "Campo de Arquivo"
        icon = "doc-full-inverse"

#FIM CAMPOS DE FORMULÁRIO

class CustomForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields_config = kwargs.pop('fields_config', None)
        super().__init__(*args, **kwargs)
        self.fields['nome_completo'] = forms.CharField(
            label="Nome Completo",
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        self.fields['titulo'] = forms.CharField(
            label="Título",
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
        if fields_config:
            for i, block in enumerate(fields_config):
                field_name = f"custom_field_{i}_{block.block_type}"
                field_label = block.value.get('label')
                is_required = block.value.get('required', False)
                help_text = block.value.get('help_text', '')
                field_type = block.block_type 

                field_class = forms.CharField
                widget = forms.TextInput(attrs={'class': 'form-control'})

                if field_type == 'texto_longo':
                    widget = forms.Textarea(attrs={'class': 'form-control'})
                elif field_type == 'email':
                    field_class = forms.EmailField
                elif field_type == 'numero':
                    field_class = forms.IntegerField
                    widget = forms.NumberInput(attrs={'class': 'form-control'})
                elif field_type == 'arquivo':
                    self.fields[field_name] = forms.FileField(label=field_label, required=is_required, help_text=help_text, validators=[validate_file_size], widget=forms.FileInput(attrs={'class': 'form-control'}))
                    continue
                elif field_type == 'menu_opcoes':
                    field_class = forms.ChoiceField
                    choices_str = block.value.get('choices', '')
                    choices = [(choice.strip(), choice.strip()) for choice in choices_str.splitlines() if choice.strip()]
                    widget = forms.Select(attrs={'class': 'form-select'})
                    self.fields[field_name] = field_class(label=field_label, required=is_required, help_text=help_text, choices=choices, widget=widget)
                    continue

                self.fields[field_name] = field_class(label=field_label, required=is_required, help_text=help_text, widget=widget)