from django import template
from avaliacoes.models import Criterio, Resposta

register = template.Library()

@register.filter(name='get_dimensoes')
def get_dimensoes(criterio):
    c = Criterio.objects.get(pk=criterio)
    return c.dimensoes.all()