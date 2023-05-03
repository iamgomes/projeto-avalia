from django.db import models
from django.contrib.auth.models import AbstractUser
from entidades.models import Municipio, Entidade
from smart_selects.db_fields import ChainedManyToManyField

class User(AbstractUser):
    FUNCAO_CHOICES = (
        ('C', 'Controlador Interno'),
        ('T', 'Tribunal de Contas'),
        ('A', 'Atricon')
    )
    
    funcao = models.CharField(max_length=1, choices=FUNCAO_CHOICES, default='C')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    entidade = ChainedManyToManyField(Entidade,
                                      chained_field="municipio",
                                      chained_model_field="municipio",
                                      auto_choose=False
                                      )
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    celular = models.CharField(max_length=15, null=True, blank=True)

    def nome_completo(self):
        return '{} {}'.format(self.first_name, self.last_name)
