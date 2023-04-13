from django.urls import path
from . import views


urlpatterns = [
    path('avaliacao/', views.avaliacao, name='avaliacao'),
    path('resposta/<int:id>/add/', views.add_resposta, name='add_resposta'),
    path('resposta/<int:id>/change/', views.change_resposta, name='change_resposta'),
    path('<int:id>/add/', views.add_usuario_avaliacao, name='add_usuario_avaliacao'),
    path('<int:id>/delete/', views.delete_usuario_avaliacao, name='delete_usuario_avaliacao'),
    path('<int:id>/envia_para_validacao/', views.envia_para_validacao, name='envia_para_validacao'),
    path('validacao/<int:id>/add/', views.add_usuario_validacao, name='add_usuario_validacao'),
    path('<int:id>/resposta_validacao/<int:id_validacao>/add/', views.add_resposta_validacao, name='add_resposta_validacao'),
    path('validacao/<int:id>/change/', views.change_resposta_validacao, name='change_resposta_validacao'),
]
