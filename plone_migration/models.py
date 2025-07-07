from django.db import models

from wagtail.documents.models import Document
from wagtail.images.models import Image

class PloneImportedImage(Image):
    """
    Extensão do modelo base de imagem do Wagtail para importar imagens do Plone.
    """
    plone_node_id = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="ID do nó da imagem no Plone.",
        null=True,
        blank=True,
    )
    slug_plone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Slug original do Plone."
    )

    admin_form_fields = Image.admin_form_fields + (
        'plone_node_id',
        'slug_plone',
    )

class PloneImportedFile(Document):
    """
    Extensão do modelo base de arquivo do Wagtail para importar arquivos do Plone.
    """
    plone_node_id = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="ID do nó do arquivo no Plone.",
        null=True,
        blank=True,
    )
    slug_plone = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Slug original do Plone."
    )

    admin_form_fields = Document.admin_form_fields + (
        'plone_node_id',
        'slug_plone',
    )