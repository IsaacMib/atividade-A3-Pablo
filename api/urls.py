from django.urls import path
from .views import SharedContentByTagAPIView, AllSharedContentAPIView

app_name = 'api'

urlpatterns = [
    path('shared-content/tag/<slug:tag_slug>/', SharedContentByTagAPIView.as_view(), name='shared_content_by_tag'),
    path('shared-content/all/', AllSharedContentAPIView.as_view(), name='all_shared_content'),
]