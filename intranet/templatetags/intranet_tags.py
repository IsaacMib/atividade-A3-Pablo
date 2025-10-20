from django import template
from intranet.models import IntranetPage

register = template.Library()


@register.simple_tag
def get_intranet_content_page(index_page):
    content_page = IntranetPage.objects.child_of(index_page).live().first()
    return content_page