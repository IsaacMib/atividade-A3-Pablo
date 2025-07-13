from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from django.views.generic import RedirectView

from search import views as search_views
from sitepadrao import views as sitepadrao_views

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
        )
]

if settings.HABILITAR_SSO_LOGIN:
    urlpatterns += [
        # Sobrescreve a URL de logout
        # path("admin/email/", login_required(sitepadrao_views.redirect_if_in_group), name="admin_email_redirect"),
        path("admin/", include("allauth.urls")),
        path('manager/login/', RedirectView.as_view(url='/admin/', permanent=True)),
        path("manager/", include(wagtailadmin_urls)),
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
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]