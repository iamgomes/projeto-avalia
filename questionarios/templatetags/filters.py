from django import template
from questionarios.models import Resposta, ItemAvaliacao

register = template.Library()

@register.filter(name='get_dimensao')
def get_dimensao(resposta):
    r = Resposta.objects.get(pk=resposta)
    item = ItemAvaliacao.objects.get(pk=r.itens_avaliacao.id)
    criterio = item.criterio_set.all().first()

    return criterio.dimensao


@register.filter(name='get_criterio')
def get_criterio(resposta):
    r = Resposta.objects.get(pk=resposta)
    item = ItemAvaliacao.objects.get(pk=r.itens_avaliacao.id)
    criterio = item.criterio_set.filter(pk=1).first()

    return criterio