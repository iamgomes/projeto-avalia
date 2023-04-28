from django.urls import path
from . import views


urlpatterns = [
    path('minhas_avaliacoes/', views.minhas_avaliacoes, name='minhas_avaliacoes'),
    path('avaliacao/', views.avaliacao, name='avaliacao'),
    path('ajax/load_motivos/', views.load_motivos, name='ajax_load_motivos'),
]
