from wagtail.blocks import (
    CharBlock,
    StructBlock,
    PageChooserBlock,
)

from django.core.exceptions import ValidationError


class ListGrupoSecretariadoBlock(StructBlock):
    """
    Block específico para grupos do Secretariado.
    Baseado em ListGrupoCorpoTecnicoBlock mas referenciando a classe concreta SecretariadoGrupoPageIndex.
    """
    titulo = CharBlock(required=False, max_length=255, label="Título do Grupo")
    grupo_page = PageChooserBlock(
        target_model="institucional.SecretariadoGrupoPageIndex",
        required=True,
        label="Selecione a página do grupo do secretariado"
    )

    class Meta:
        label = "Grupo do Secretariado"
        icon = "group"