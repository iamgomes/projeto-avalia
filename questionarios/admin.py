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
    ordering = ('cod',)
    list_filter = ('exigibilidade', 'dimensao',)
    list_display = ['cod','criterio_texto', 'exigibilidade', 'dimensao', 'avaliacao']

admin.site.register(Criterio, CriterioAdmin)

class CriterioItemAdmin(admin.ModelAdmin):
    ordering = ('criterio',)
    list_display = ['criterio', 'item_avaliacao']

admin.site.register(CriterioItem, CriterioItemAdmin)

class DimensaoAdmin(admin.ModelAdmin):
    list_display = ['dimensao_texto', 'peso']

admin.site.register(Dimensao, DimensaoAdmin)

class ItemAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['item_avaliacao', 'peso']

admin.site.register(ItemAvaliacao, ItemAvaliacaoAdmin)

admin.site.register(ImagemEvidencia)
admin.site.register(JustificativaEvidencia)
admin.site.register(LinkEvidencia)
admin.site.register(Tramitacao)