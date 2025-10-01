from django.db import models
from core.models import PageSitePadrao, PageSitePadraoIndex
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from blocks.institucional import LocalizacaoBlock

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your models here.

class InstitucionalIndexPage(PageSitePadraoIndex):
    """
    Página de índice para o conteúdo institucional.
    """
    
    subpage_types = ['institucional.LocalizacaoPage']

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

class SecretariadoIndex(PageSitePadraoIndex):
    """
    Página de índice para o conteúdo do Secretariado.
    """

    pass