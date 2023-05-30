from django.urls import path
from . import views


urlpatterns = [
    path('minhas_avaliacoes/', views.minhas_avaliacoes, name='minhas_avaliacoes'),
    path('minhas_validacoes/', views.minhas_validacoes, name='minhas_validacoes'),
    path('avaliacoes_setor/', views.avaliacoes_setor, name='avaliacoes_setor'),
    path('projetos_disponiveis/', views.projetos_disponiveis, name='projetos_disponiveis'),
    path('ajax/load_motivos/', views.load_motivos, name='ajax_load_motivos'),
]
