from django.conf import settings
from django.contrib.auth.models import Group
from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets import viewsets
from wagtail.users.forms import UserCreationForm, UserEditForm
from .models import IntegrationUser


class CustomIntegrationUserCreationForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
            user.groups.add(integration_group)
        return user

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name", "last_name", "email", "is_active")


class CustomIntegrationUserEditForm(UserEditForm):
    class Meta(UserEditForm.Meta):
        fields = ("username", "first_name", "last_name", "email", "is_active")


class IntegrationUserAdmin(ModelViewSet):
    model = IntegrationUser
    menu_label = "Usuários de Integração"
    name = "integration_users"
    icon = "plus"
    menu_order = 800
    add_to_settings_menu = True
    list_display = ("username", "email", "first_name", "last_name", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    def get_form_class(self, for_update=False):
        if for_update:
            return CustomIntegrationUserEditForm
        return CustomIntegrationUserCreationForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(groups__name='Usuário de integração')


if settings.PORTAL_PROVEDOR_CONTEUDO:
    viewsets.register(IntegrationUserAdmin())