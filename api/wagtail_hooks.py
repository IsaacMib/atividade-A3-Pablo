# from wagtail.admin.viewsets.model import (
#     ModelViewSet,
# )
# from wagtail.admin.viewsets import viewsets
# from rest_framework.authtoken.models import TokenProxy as Token
#
#
# class TokenAdmin(ModelViewSet):
#     model = Token
#     menu_label = "Tokens da API"
#     menu_icon = "binary"
#     menu_order = 900
#     add_to_admin_menu = True
#     list_display = ("user", "key", "created")
#     list_filter = ("user",)
#     search_fields = ("user__username",)
#     exclude_form_fields = ('key',)
#
#
# viewsets.register(TokenAdmin())