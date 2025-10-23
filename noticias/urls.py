from django.urls import path
from . import views

urlpatterns = [
    path('remota/<int:noticia_id>/', views.noticia_remota_detail_view, name='noticia_remota_detail'),
]