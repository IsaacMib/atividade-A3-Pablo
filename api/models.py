from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class IntegrationUser(User):
    class Meta:
        proxy = True
        verbose_name = "Usuário de Integração"
        verbose_name_plural = "Usuários de Integração"
