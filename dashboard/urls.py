from django.urls import path
from . import views

urlpatterns = [
    path('', views.visao_geral, name='visao_geral'),
    path('exporta_csv_visao_geral/', views.exporta_csv_visao_geral, name='exporta_csv_visao_geral')
]