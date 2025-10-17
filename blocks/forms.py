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
        self.fields_config = fields_config
        self.request = kwargs.pop('request', None)
        self.show_recaptcha = kwargs.pop('show_recaptcha', False)
        self.recaptcha_secret_key = kwargs.pop('recaptcha_secret_key', None)

        super().__init__(*args, **kwargs)
        self.fields['nome_completo'] = forms.CharField(
            label="Nome Completo",
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            error_messages={'required': 'Por favor, informe seu nome completo.'}
        )
        self.fields['titulo'] = forms.CharField(
            label="Título",
            required=True,
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            error_messages={'required': 'Por favor, informe um título para sua mensagem.'}
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
                field_error_messages = {'required': 'Por favor, preencha este campo.'}

                if field_type == 'texto_longo':
                    widget = forms.Textarea(attrs={'class': 'form-control'})
                elif field_type == 'email':
                    field_class = forms.EmailField
                    field_error_messages = {
                        'required': 'Por favor, informe um endereço de e-mail.',
                        'invalid': 'Informe um e-mail válido (ex: nome@exemplo.com).'
                    }
                elif field_type == 'numero':
                    field_class = forms.IntegerField
                    widget = forms.NumberInput(attrs={'class': 'form-control'})
                    field_error_messages = {
                        'required': 'Por favor, informe um número.',
                        'invalid': 'Informe um número inteiro válido.'
                    }
                elif field_type == 'arquivo':
                    self.fields[field_name] = forms.FileField(
                        label=field_label,
                        required=is_required,
                        help_text=help_text,
                        validators=[validate_file_size],
                        widget=forms.FileInput(attrs={'class': 'form-control'}),
                        error_messages={'required': 'Por favor, envie um arquivo.'}
                    )
                    continue
                elif field_type == 'menu_opcoes':
                    field_class = forms.ChoiceField
                    choices_str = block.value.get('choices', '')
                    choices = [(choice.strip(), choice.strip()) for choice in choices_str.splitlines() if choice.strip()]
                    widget = forms.Select(attrs={'class': 'form-select'})
                    self.fields[field_name] = field_class(
                        label=field_label,
                        required=is_required,
                        help_text=help_text,
                        choices=choices,
                        widget=widget,
                        error_messages={'required': 'Selecione uma opção válida.'}
                    )
                    continue

                field_kwargs = {
                    'label': field_label,
                    'required': is_required,
                    'help_text': help_text,
                    'widget': widget,
                    'error_messages': field_error_messages
                }

                self.fields[field_name] = field_class(**field_kwargs)

        if self.show_recaptcha:
            self.fields['g-recaptcha-response'] = forms.CharField(
                required=True,
                widget=forms.HiddenInput()
            )

    def clean(self):
        cleaned_data = super().clean()
        if self.show_recaptcha:
            token = cleaned_data.get('g-recaptcha-response')
            if not token:
                raise forms.ValidationError('reCAPTCHA não verificado.')
            try:
                import requests
                secret = self.recaptcha_secret_key
                if not secret:
                    raise forms.ValidationError('ReCAPTCHA não configurado no servidor.')
                resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                    'secret': secret,
                    'response': token,
                    'remoteip': self.request.META.get('REMOTE_ADDR') if self.request else ''
                }, timeout=5)
                result = resp.json() if resp.status_code == 200 else {}
                if not result.get('success'):
                    raise forms.ValidationError('Falha na validação do reCAPTCHA.')
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError('Erro ao validar reCAPTCHA. Tente novamente.')

        return cleaned_data