from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/add/', views.add_validacao, name='add_validacao'),
    path('<int:id>/change/', views.change_resposta_validacao, name='change_resposta_validacao'),
    path('<int:id>/delete/', views.delete_validacao, name='delete_validacao'),
    path('<int:id>/resposta/<int:id_validacao>/add/', views.add_resposta_validacao, name='add_resposta_validacao'),
    path('imagem/<int:id>/delete/', views.delete_imagem_validacao, name='delete_imagem_validacao'),
]