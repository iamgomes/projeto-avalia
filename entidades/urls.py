from django.urls import path
from . import views

urlpatterns = [
    path('municipio_bulk/', views.MunicipioBulk.as_view(), name='municipio_bulk')
]
