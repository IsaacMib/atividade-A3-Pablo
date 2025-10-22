from django.urls import path
from .views import SharedContentByTagAPIView, AllSharedContentAPIView
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api'

urlpatterns = [
    path('get-token/', obtain_auth_token, name='get_token'),

    path('shared-content/tag/<slug:tag_slug>/', SharedContentByTagAPIView.as_view(), name='shared_content_by_tag'),
    path('shared-content/all/', AllSharedContentAPIView.as_view(), name='all_shared_content'),
]