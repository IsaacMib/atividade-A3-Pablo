from django.urls import path
from .views import SharedContentByTagAPIView, AllSharedContentAPIView, SingleNoticiaAPIView
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_exempt

app_name = 'api'

urlpatterns = [
    path('get-token/', csrf_exempt(obtain_auth_token), name='get_token'),

    path('shared-content/noticia/<int:pk>/', SingleNoticiaAPIView.as_view(), name='single_noticia_content'),
    path('shared-content/tag/<slug:tag_slug>/', SharedContentByTagAPIView.as_view(), name='shared_content_by_tag'),
    path('shared-content/all/', AllSharedContentAPIView.as_view(), name='all_shared_content'),
]