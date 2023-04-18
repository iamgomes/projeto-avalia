from django.urls import path
from . import views

urlpatterns = [
    path('resposta/<int:id>/add/', views.add_resposta, name='add_resposta'),
    path('resposta/<int:id>/change/', views.change_resposta, name='change_resposta'),
    path('<int:id>/add/', views.add_questionario, name='add_questionario'),
    path('<int:id>/delete/', views.delete_questionario, name='delete_questionario'),
]