from django.contrib.auth.models import Group
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.viewsets import viewsets
from wagtail.users.forms import UserCreationForm, UserEditForm
from .models import IntegrationUser


class CustomIntegrationUserCreationForm(UserCreationForm):
    """Formulário de criação com ordem de campos e grupos ocultos."""
    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name", "last_name", "email", "is_active")


class CustomIntegrationUserEditForm(UserEditForm):
    """Formulário de edição com ordem de campos e grupos ocultos."""
    class Meta(UserEditForm.Meta):
        fields = ("username", "first_name", "last_name", "email", "is_active")


class IntegrationUserAdmin(ModelViewSet):
    model = IntegrationUser
    menu_label = "Usuários de Integração"
    name = "integration_users"
    icon = "users"
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

    def save_instance(self, instance, form, is_new):
        user = super().save_instance(instance, form, is_new)
        if is_new:
            integration_group, _ = Group.objects.get_or_create(name='Usuário de integração')
            user.groups.add(integration_group)
        return user

viewsets.register(IntegrationUserAdmin())