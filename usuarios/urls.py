from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('foto/', views.change_foto, name='change_foto'),
    path('add_usuario/', views.add_usuario, name='add_usuario')
]