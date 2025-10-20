from django.urls import path, reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import logout

# Fake login OIDC
def fake_oidc_login(request, provider_id=None):
    return redirect(reverse_lazy("wagtailadmin_login"))

# Logout da intranet
def intranet_logout(request):
    logout(request)
    return redirect("/")

urlpatterns = [
    path(
        "openid_connect/login/<str:provider_id>/",
        fake_oidc_login,
        name="openid_connect_login",
    ),
    path(
        "logout/",
        intranet_logout,
        name="intranet_logout",
    ),
]
