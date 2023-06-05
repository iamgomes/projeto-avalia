from django.db import models
from django.contrib.auth.models import AbstractUser
from entidades.models import Municipio, Entidade
from smart_selects.db_fields import ChainedManyToManyField
from django.dispatch import receiver
from django.db.models.signals import post_save
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.permissions import grant_permission, revoke_permission


class User(AbstractUser):
    SETOR_CHOICES = (
        ('C', 'Controle Interno'),
        ('T', 'Tribunal de Contas'),
        ('A', 'Atricon')
    )

    FUNCAO_CHOICES = (
        ('A', 'Avaliador'),
        ('V', 'Validador'),
        ('C', 'Coordenador')
    )
    
    setor = models.CharField(max_length=1, choices=SETOR_CHOICES, default='C')
    funcao = models.CharField(max_length=1, choices=FUNCAO_CHOICES, default='A')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    entidade = ChainedManyToManyField(Entidade,
                                      chained_field="municipio",
                                      chained_model_field="municipio",
                                      auto_choose=True
                                      )
    foto = models.ImageField(upload_to='perfil/', null=True, blank=True)
    celular = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)

    def nome_completo(self):
        return '{} {}'.format(self.first_name, self.last_name)
    
    class Meta:
        ordering = ('first_name', )


@receiver(post_save, sender=User)
def define_permissoes(sender, instance, created, **kwargs):
    if created:
        if instance.funcao == 'A':
            assign_role(instance, 'avaliadores')
        if instance.funcao == 'V':
            assign_role(instance, 'validadores')
        elif instance.funcao == 'C':
            assign_role(instance, 'coordenadores')