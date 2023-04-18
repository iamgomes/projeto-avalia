from django.contrib import admin
from .models import Criterio, Questionario, Resposta, Dimensao, Tramitacao, \
                    ImagemEvidencia, ItemAvaliacao, LinkEvidencia, CriterioItem


class QuestionarioAdmin(admin.ModelAdmin):
    list_display = ['avaliacao', 'usuario', 'entidade', 'status']
    
admin.site.register(Questionario, QuestionarioAdmin)

class RespostaoAdmin(admin.ModelAdmin):
    list_display = ['resposta', 'questionario', 'nota']

admin.site.register(Resposta, RespostaoAdmin)

class CriterioAdmin(admin.ModelAdmin):
    list_display = ['criterio_texto', 'exigibilidade', 'dimensao', 'avaliacao']

admin.site.register(Criterio, CriterioAdmin)

admin.site.register(Dimensao)
admin.site.register(ImagemEvidencia)
admin.site.register(ItemAvaliacao)
admin.site.register(LinkEvidencia)
admin.site.register(CriterioItem)
admin.site.register(Tramitacao)