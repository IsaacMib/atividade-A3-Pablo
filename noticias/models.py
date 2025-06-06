from django.db import models

from django.contrib import messages
from django.shortcuts import redirect, render
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import FieldPanel, MultipleChooserPanel
from wagtail.fields import StreamField
from wagtail.search import index

from wagtail.models import Orderable, Page

from blocks.models import BaseStreamBlock
from datetime import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


class NoticiasPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the BlogPage object and tags. There's a longer guide on using it at
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        "NoticiasPage", related_name="tagged_items", on_delete=models.CASCADE
    )

class NoticiasPage(Page):
    
    subtitle = models.CharField(verbose_name="Subtítulo",blank=True, max_length=255)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    descricao = models.CharField(
        verbose_name="Descrição",
        blank=True,
        max_length=255,
        help_text="Breve descrição do conteúdo da página.",
    )
    data_publicacao = models.DateTimeField("Data de publicação da notícias", default=datetime.now, blank=True, null=True)
    tags = ClusterTaggableManager(through=NoticiasPageTag, blank=True)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, null=True, use_json_field=True
    )

    body_migrated = models.TextField(
        help_text="Usado apenas para conteúdo do antigo site Plone.",
        null=True,
        blank=True,
    )
    plone_node_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("descricao"),
        FieldPanel("image"),
        FieldPanel("body"),
        FieldPanel("data_publicacao"),
        FieldPanel("tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the blog post into a list we can access on the template.
        We're additionally adding a URL to access BlogPage objects with that tag
        """
        tags = self.tags.all()
        base_url = self.get_parent().url
        for tag in tags:
            tag.url = f"{base_url}tags/{tag.slug}/"
        return tags
    
    # Specifies parent to NoticiasPage as being NoticiasIndexPages
    parent_page_types = ["NoticiasIndexPages"]

    # Specifies what content types can exist as children of NoticiasPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []

    def get_ultimas_noticias(self, quantidade=6):
        return NoticiasPage.objects.live().order_by("-data_publicacao")[:quantidade]

    def get_context(self, request):
        context = super().get_context(request)
        context["ultimas_noticias"] = self.get_ultimas_noticias()
        
        return context

class NoticiasIndexPages(RoutablePageMixin, Page):

    introduction = models.TextField(help_text="Texto para o topo da notícia", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    max_count = 1

    parent_page_types = [
        "home.HomePage",
    ]

    # Specifies that only BlogPage objects can live under this index page
    subpage_types = ["NoticiasPage"]

    # Defines a method to access the children of the page (e.g. BlogPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()
    
    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(NoticiasIndexPages, self).get_context(request)
        all_posts = NoticiasPage.objects.descendant_of(self).live().order_by("-data_publicacao")
        paginator = Paginator(all_posts, 12) # Show 12 posts per page
        page = request.GET.get("page")
        try:
            # If the page exists and the ?page=x is an int
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If the ?page=x is not an int; show the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If the ?page=x is out of range (too high most likely)
            # Then return the last page
            posts = paginator.page(paginator.num_pages)
        context["posts"] = posts
        return context
    
     # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no blog posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {"self": self, "tag": tag, "posts": posts}
        return render(request, "noticias/noticias_index_pages.html", context)
    
    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)
    
    # Returns the child BlogPage objects for this BlogPageIndex.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = NoticiasPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts
    
    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not tags.append() because we don't want a list of lists
            tags += post.get_tags
        tags = sorted(set(tags))
        return tags
    
    def get_ultimas_noticias(self, quantidade=6):
        return NoticiasPage.objects.live().descendant_of(self).order_by('-data_publicacao')[:quantidade]