from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Questionario

@receiver(post_save, sender=Questionario)
def update_indice(sender, instance, created, **kwargs):
    print(f'Vc alterou a avaliacao {instance.id}')
    indice = instance.nota
    nivel = instance.classificacao
    essenciais = instance.percentual_atendido_essenciais
    Questionario.objects.filter(pk=instance.id).update(indice=indice, nivel=nivel, essenciais=essenciais)