from django.urls import path
from . import views

urlpatterns = [
    path('lista_notificacoes/', views.lista_notificacoes, name='lista_notificacoes'),
    path('all_notificacao_lida/', views.all_notificacao_lida, name='all_notificacao_lida'),
    path('<int:id>/delete/', views.delete_notificacao, name='delete_notificacao'),
]