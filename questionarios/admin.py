from django.contrib import admin
from .models import Criterio, Questionario, Resposta, Dimensao, Tramitacao,\
                    ImagemEvidencia, ItemAvaliacao, LinkEvidencia, CriterioItem, JustificativaEvidencia


class QuestionarioAdmin(admin.ModelAdmin):
    list_display = ['avaliacao', 'usuario', 'entidade', 'status', 'essenciais','indice', 'nivel']
    list_filter = ('status', 'nivel',)
    search_fields = ['entidade__nome','usuario__username']
    
admin.site.register(Questionario, QuestionarioAdmin)

class RespostaoAdmin(admin.ModelAdmin):
    list_display = ['resposta', 'questionario', 'nota']

admin.site.register(Resposta, RespostaoAdmin)

class CriterioAdmin(admin.ModelAdmin):
    ordering = ('cod',)
    list_filter = ('exigibilidade', 'matriz', 'dimensao',)
    list_display = ['criterio_texto', 'cod', 'matriz', 'exigibilidade', 'dimensao', 'avaliacao']

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

class TramitacaoAdmin(admin.ModelAdmin):
    list_display = ['questionario', 'setor', 'motivo','usuario', 'created_at']
    search_fields = ['questionario__entidade__nome','usuario__username']

admin.site.register(Tramitacao, TramitacaoAdmin)

admin.site.register(ImagemEvidencia)
admin.site.register(JustificativaEvidencia)
admin.site.register(LinkEvidencia)
