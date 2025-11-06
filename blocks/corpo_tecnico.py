from wagtail.blocks import (
    CharBlock,
    StructBlock
)

class ListGrupoCorpoTecnicoBlock(StructBlock):
    titulo = CharBlock(required=False, max_length=255, label="Título do Grupo")
    # PageChooserBlock comentado pois referencia classe abstrata
    # Deve ser reimplementado nas apps que usarem as classes concretas
    # grupo_page = PageChooserBlock(
    #     target_model="paginas.CorpoTecnicoGrupoPageIndex",
    #     required=True,
    #     label="Selecione a página do grupo"
    # )
