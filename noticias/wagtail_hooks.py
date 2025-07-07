from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail import hooks

@hooks.register('register_permissions')
def register_custom_permissions():
    noticia_ct = ContentType.objects.get(app_label='noticias', model='noticiaspage')
    return Permission.objects.filter(
        content_type=noticia_ct,
        codename='view_conteudo_migrado'
    )