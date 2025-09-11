from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from wagtail import hooks
from django.utils.html import format_html


@hooks.register('register_permissions')
def register_custom_permissions():
    noticia_ct = ContentType.objects.get(
        app_label='noticias', model='noticiaspage')
    return Permission.objects.filter(
        content_type=noticia_ct,
        codename='view_conteudo_migrado'
    )


@hooks.register("insert_editor_js")
def char_counter_js():
    return format_html('<script src="/static/js/charcount.js"></script>')


@hooks.register("insert_editor_css")
def char_counter_css():
    return format_html('<link rel="stylesheet" href="/static/css/charcount.css">')
