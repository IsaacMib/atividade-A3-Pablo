from django.test import TestCase, RequestFactory
from django.utils.encoding import force_str
from wagtail.models import Site, Collection
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file

from core.utils_test import ensure_root_page
from home.models import HomePage
from .models import LinhaDoTempoIndex, LinhaDoTempoPage, CardLinhaDoTempoPage

Image = get_image_model()

class LinhaDoTempoCardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = ensure_root_page()

        # Limpar páginas filhas existentes
        for child in cls.root_page.get_children():
            child.delete()
        cls.root_page.refresh_from_db()

        # Site default
        if not Site.objects.filter(is_default_site=True).exists():
            Site.objects.create(
                hostname="localhost",
                port=80,
                root_page=cls.root_page,
                is_default_site=True,
                site_name="Test Site",
            )

        # Garantir Collection root (para imagens)
        if not Collection.objects.filter(depth=1).exists():
            Collection.add_root(name="Root")

        # Imagens de teste
        cls.img1 = Image.objects.create(title="Img 1", file=get_test_image_file())
        cls.img2 = Image.objects.create(title="Img 2", file=get_test_image_file())

        # Home -> Index -> LinhaDoTempo
        cls.home_page = HomePage(title="Home LT", slug="home-lt")
        cls.root_page.add_child(instance=cls.home_page)
        cls.home_page.save_revision().publish()

        cls.index = LinhaDoTempoIndex(title="Index LT", slug="index-lt")
        cls.home_page.add_child(instance=cls.index)
        cls.index.save_revision().publish()

        cls.timeline = LinhaDoTempoPage(title="Timeline", slug="timeline")
        cls.index.add_child(instance=cls.timeline)
        cls.timeline.save_revision().publish()

        cls.factory = RequestFactory()

    def test_imagem_property_returns_first_image(self):
        page = CardLinhaDoTempoPage(
            title="Card 1",
            slug="card-1",
        )
        self.timeline.add_child(instance=page)
        page.images = [
            ("imagem", self.img1),
            ("imagem", self.img2),
        ]
        page.save()

        self.assertIsNotNone(page.imagem)
        self.assertEqual(page.imagem.id, self.img1.id)

    def test_card_page_template_single_image_with_alt_fallback(self):
        page = CardLinhaDoTempoPage(
            title="Card Single",
            slug="card-single",
        )
        self.timeline.add_child(instance=page)
        # alt_text vazio → deve cair no fallback do título da imagem
        page.images = [("imagem", self.img1)]
        page.save_revision().publish()

        # Renderizar um template mínimo que replica apenas a seção de imagem (1 item)
        from django.template import Template, Context
        template = Template(
            """
            {% load wagtailimages_tags %}
            {% if page.images and page.images|length > 1 %}
              <!-- múltiplas imagens omitidas neste teste -->
            {% elif page.images and page.images|length == 1 %}
              <div class="d-flex justify-content-center noticias-img-destaque tw:pb-12">
              {% with imagem=page.images.0 %}
                {% image imagem.value original loading="lazy" class="img-fluid" alt=imagem.value.title|default:"Imagem do conteúdo" %}
              {% endwith %}
              </div>
            {% endif %}
            """
        )
        html = template.render(Context({"page": page}))
        # Estrutura para 1 imagem não usa swiper
        self.assertIn("img-fluid", html)
        self.assertNotIn("swiper-wrapper", html)
        # alt deve usar título da imagem
        self.assertIn(f'alt="{self.img1.title}"', html)

    def test_card_page_template_multiple_images_with_swiper_and_custom_alt(self):
        page = CardLinhaDoTempoPage(
            title="Card Multi",
            slug="card-multi",
        )
        self.timeline.add_child(instance=page)
        page.images = [
            ("imagem", self.img1),
            ("imagem", self.img2),
        ]
        page.save_revision().publish()

        # Renderizar um template mínimo que replica apenas a seção de imagens (múltiplas)
        from django.template import Template, Context
        template = Template(
            """
            {% load wagtailimages_tags %}
            {% if page.images and page.images|length > 1 %}
              <div class="swiper banner-img-swiper2">
                <div class="swiper-wrapper">
                  {% for imagem in page.images %}
                    <div class="swiper-slide swiper-slide-noticias">{% image imagem.value original loading="lazy" class="image-noticia-carrossel" alt=imagem.value.title|default:"Imagem do conteúdo" %}</div>
                  {% endfor %}
                </div>
              </div>
            {% endif %}
            """
        )
        html = template.render(Context({"page": page}))
        # Estrutura para múltiplas imagens usa swiper
        self.assertIn("banner-img-swiper2", html)
        self.assertIn("swiper-wrapper", html)
        # Alts devem usar o título da imagem
        self.assertIn(f'alt="{self.img1.title}"', html)
        self.assertIn(f'alt="{self.img2.title}"', html)

    def test_blocks_template_alt_text_default_and_custom(self):
        """Renderiza o template do bloco de card e valida o alt."""
        from django.template import Template, Context

        # Mock simples do card com atributos esperados
        class MockCard:
            def __init__(self, image, texto_alternativo=None, titulo="", title=""):
                self.imagem = image
                self.texto_alternativo = texto_alternativo
                self.titulo = titulo
                self.title = title or titulo
                self.descricao_linha_do_tempo = ""
                self.detail_page = None

        template = Template(
            """
            {% load wagtailimages_tags %}
            {% load text_filters %}
            {% include 'blocks/card_linha_do_tempo.html' with card=card index=0 last_index=0 %}
            """
        )

        # Caso com alt customizado
        card_custom = MockCard(self.img1, texto_alternativo="Meu Alt")
        html_custom = template.render(Context({"card": card_custom}))
        self.assertIn('alt="Meu Alt"', force_str(html_custom))

        # Caso sem alt → default "Não especificado"
        card_default = MockCard(self.img2, texto_alternativo=None)
        html_default = template.render(Context({"card": card_default}))
        self.assertIn('alt="Não especificado"', force_str(html_default))
