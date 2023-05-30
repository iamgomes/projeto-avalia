from django.urls import path
from . import views

urlpatterns = [
    path('', views.visao_geral, name='visao_geral'),
]