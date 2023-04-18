from django.db import models
from django.contrib.auth.models import AbstractUser
from entidades.models import Municipio, Entidade

class User(AbstractUser):
    FUNCAO_CHOICES = (
        ('C', 'Controlador Interno'),
        ('A', 'Auditor')
    )
    
    funcao = models.CharField(max_length=1, choices=FUNCAO_CHOICES, default='C')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    entidade = models.ManyToManyField(Entidade)
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
