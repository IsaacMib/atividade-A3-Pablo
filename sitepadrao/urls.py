from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from django.views.generic import RedirectView

from django.conf.urls import handler404, handler500
from django.shortcuts import render

from search import views as search_views
from sitepadrao import views as sitepadrao_views
from . import views

handler403 = 'sitepadrao.views.erro_403'
handler404 = 'sitepadrao.views.erro_404'
handler500 = 'sitepadrao.views.erro_500'

urlpatterns = [
    path("health/", sitepadrao_views.health_check, name='health_check'),
    path("django-admin/", admin.site.urls),
    path("documents/", include(wagtaildocs_urls)),
    re_path(
        r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
        ServeView.as_view(),
        name="wagtailimages_serve",
    ),
    path("search/", search_views.search, name="search"),
    path("__reload__/", include("django_browser_reload.urls")),
    path(
            "favicon.ico",
            RedirectView.as_view(url=settings.STATIC_URL + "img/favicon.ico"),
        ),
    path("acesso_negado/", sitepadrao_views.acesso_negado, name="acesso_negado"),
    path("404/", sitepadrao_views.erro_404, name="erro_404"),
]

if settings.HABILITAR_SSO_LOGIN:
    urlpatterns += [
        # Sobrescreve a URL de logout do Wagtail admin para incluir logout do SSO
        path("admin/manager/logout/", sitepadrao_views.wagtail_logout_with_sso, name="wagtailadmin_logout"),
        # path("admin/email/", login_required(sitepadrao_views.redirect_if_in_group), name="admin_email_redirect"),
        path('admin/manager/login/', RedirectView.as_view(url='/admin/', permanent=True)),
        path("admin/manager/", include(wagtailadmin_urls)),
        path("admin/", include("allauth.urls")),
        
    ]
else:
    urlpatterns += [
        path("admin/", include(wagtailadmin_urls)),
    ]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("intranet/", include("intranet.urls")),
    path("", include('wagtail.urls')),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

def erro_500(request):
    return render(request, "500.html", status=500)

handler500 = erro_500