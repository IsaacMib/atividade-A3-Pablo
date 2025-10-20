from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver


@receiver(pre_social_login)
def handle_new_sso_user(sender, request, sociallogin, **kwargs):
    if not sociallogin.is_existing:
        user = sociallogin.user
        user.is_staff = False
        user.is_superuser = False
        try:
            extra_data = sociallogin.account.extra_data
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        except (KeyError, AttributeError):
            pass