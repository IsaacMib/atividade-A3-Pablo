from wagtail import blocks


class TituloBlock(blocks.StructBlock):
   """Bloco de título com opções de estilo e visibilidade."""
   titulo = blocks.CharBlock(
       required=True,
       help_text='Digite o título que será exibido'
   )
   bgAzul = blocks.BooleanBlock(
       required=False,
       default=False,
       help_text='Marque para usar fundo azul com texto branco. Deixe desmarcado para texto azul com fundo branco.'
   )
   class Meta:
       template = 'blocks/titulo.html'
       icon = 'title'
       label = 'Título'