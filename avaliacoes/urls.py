from django.urls import path
from . import views


urlpatterns = [
    path('minhas_avaliacoes/', views.minhas_avaliacoes, name='minhas_avaliacoes'),
    path('avaliacao/', views.avaliacao, name='avaliacao'),
    path('<int:id>/envia_para_validacao/', views.envia_para_validacao, name='envia_para_validacao'),
]
