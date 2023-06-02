from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Validacao

@receiver(post_save, sender=Validacao)
def update_indice_validacao(sender, instance, created, **kwargs):
    print(f'Vc alterou a validacao {instance.id}')
    indice = instance.nota_validacao
    nivel = instance.classificacao_validacao
    essenciais = instance.percentual_atendido_essenciais
    Validacao.objects.filter(pk=instance.id).update(indice=indice, nivel=nivel, essenciais=essenciais)