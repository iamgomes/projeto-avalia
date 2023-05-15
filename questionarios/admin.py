from django.contrib import admin
from .models import Criterio, Questionario, Resposta, Dimensao, Tramitacao,\
                    ImagemEvidencia, ItemAvaliacao, LinkEvidencia, CriterioItem, JustificativaEvidencia


class QuestionarioAdmin(admin.ModelAdmin):
    list_display = ['avaliacao', 'usuario', 'entidade', 'status']
    
admin.site.register(Questionario, QuestionarioAdmin)

class RespostaoAdmin(admin.ModelAdmin):
    list_display = ['resposta', 'questionario', 'nota']

admin.site.register(Resposta, RespostaoAdmin)

class CriterioAdmin(admin.ModelAdmin):
    list_display = ['cod','criterio_texto', 'exigibilidade', 'dimensao', 'avaliacao']

admin.site.register(Criterio, CriterioAdmin)

class CriterioItemAdmin(admin.ModelAdmin):
    list_display = ['criterio', 'item_avaliacao']

admin.site.register(CriterioItem, CriterioItemAdmin)

admin.site.register(Dimensao)
admin.site.register(ImagemEvidencia)
admin.site.register(JustificativaEvidencia)
admin.site.register(ItemAvaliacao)
admin.site.register(LinkEvidencia)
admin.site.register(Tramitacao)