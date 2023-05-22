from django.urls import path
from . import views


urlpatterns = [
    path('minhas_avaliacoes/', views.minhas_avaliacoes, name='minhas_avaliacoes'),
    path('avaliacoes_setor/', views.avaliacoes_setor, name='avaliacoes_setor'),
    path('avaliacoes_disponiveis/', views.avaliacoes_disponiveis, name='avaliacoes_disponiveis'),
    path('ajax/load_motivos/', views.load_motivos, name='ajax_load_motivos'),
]
