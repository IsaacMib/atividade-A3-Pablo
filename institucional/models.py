from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from blocks.institucional import LocalizacaoBlock

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from paginas.models import CorpoTecnicoIndexPage, CorpoTecnicoGrupoPageIndex, CorpoTecnicoPage, PaginaComBannerPage, RichTextPage
from .blocks import ListGrupoSecretariadoBlock

class InstitucionalIndexPage(PageSitePadraoIndex):
    """
    Página de índice para o conteúdo institucional.
    """
    
    subpage_types = ['institucional.LocalizacaoPage','institucional.SecretariadoIndex', 'institucional.ComiteDeEticaPage', 'institucional.AEmpresaPage']

    parent_page_types = [ 'home.HomePage' ]

    def get_context(self, request):
        context = super(InstitucionalIndexPage, self).get_context(request)
        all_posts = self.get_children().live().public().order_by('-first_published_at')
        paginator = Paginator(all_posts, 10)  # 10 posts por página
        page_number = request.GET.get('page')
        try:
            all_posts = paginator.page(page_number)
        except PageNotAnInteger:
            all_posts = paginator.page(1)
        except EmptyPage:
            all_posts = paginator.page(paginator.num_pages)
        # Adiciona os posts ao contexto
        context['posts'] = all_posts
        return context

    class Meta:
        verbose_name = "Página Index Institucional"
        verbose_name_plural = "Páginas Institucionais"


class LocalizacaoPage(PageSitePadrao):

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    
    body = StreamField([
        ("localizacoes", LocalizacaoBlock()),
    ],
    blank=True,
    use_json_field=True,
    verbose_name="Conteúdo da página"
    )

    content_panels = PageSitePadrao.content_panels + [
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = "Página de Localização"
        verbose_name_plural = "Páginas de Localização"

class SecretariadoIndex(CorpoTecnicoIndexPage):
    """
    Página de índice para o conteúdo do Secretariado.
    """

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    subpage_types = ['institucional.SecretariadoGrupoPageIndex']
    
    template = 'paginas/corpo_tecnico_index_page.html'

    # Sobrescreve o campo grupos_corpo_tecnico para usar o block específico do Secretariado
    grupos_corpo_tecnico = StreamField(
        [
            ('grupo', ListGrupoSecretariadoBlock(label="Grupo do Secretariado")),
        ],
        verbose_name="Grupos do Secretariado",
        null=True,
        blank=True,
    )

    content_panels = CorpoTecnicoIndexPage.content_panels + [
        FieldPanel('grupos_corpo_tecnico'),
    ]

class SecretariadoGrupoPageIndex(CorpoTecnicoGrupoPageIndex):
    """
    Página de índice para os grupos do Secretariado.
    """

    parent_page_types = [ 'institucional.SecretariadoIndex' ]
    subpage_types = ['institucional.SecretariadoPage']

    template = 'paginas/corpo_tecnico_grupo_page_index.html'

class SecretariadoPage(CorpoTecnicoPage):
    """
    Página para os membros do Secretariado.
    """

    parent_page_types = [ 'institucional.SecretariadoGrupoPageIndex' ]

    template = 'paginas/corpo_tecnico_page.html'

class ComiteDeEticaPage(PaginaComBannerPage):
    template = "paginas/pagina_com_banner_page.html"

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    subpage_types = []

    class Meta:
        verbose_name = "Comitê de Ética"
        verbose_name_plural = "Comitês de Ética"

class AEmpresaPage(RichTextPage):
    template = "paginas/rich_text_page.html"

    parent_page_types = [ 'institucional.InstitucionalIndexPage' ]
    subpage_types = []

    class Meta:
        verbose_name = "Página A Empresa"
        verbose_name_plural = "Páginas A Empresa"