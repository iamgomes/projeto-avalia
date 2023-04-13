from django.contrib import admin
from .models import Avaliacao, Criterio, UsuarioAvaliacao, Resposta, Dimensao, \
                    CriterioDimensao, ImagemEvidencia, GrupoCriterio, GrupoAvaliacao, \
                    UsuarioAvaliacaoValidacao, RespostaValidacao


class CriterioDimensaoAdmin(admin.ModelAdmin):
    list_display = ['criterio', 'dimensao']

admin.site.register(CriterioDimensao, CriterioDimensaoAdmin)


class UsuarioAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['avaliacao', 'usuario', 'entidade', 'status']
    
admin.site.register(UsuarioAvaliacao, UsuarioAvaliacaoAdmin)

class RespostaoAdmin(admin.ModelAdmin):
    list_display = ['resposta', 'criterio_dimensao', 'usuarioavaliacao', 'nota']

admin.site.register(Resposta, RespostaoAdmin)

class CriterioAdmin(admin.ModelAdmin):
    list_display = ['criterio_texto', 'exigibilidade', 'grupo', 'avaliacao']

admin.site.register(Criterio, CriterioAdmin)

admin.site.register(Avaliacao)
admin.site.register(Dimensao)
admin.site.register(ImagemEvidencia)
admin.site.register(GrupoCriterio)
admin.site.register(GrupoAvaliacao)
admin.site.register(UsuarioAvaliacaoValidacao)
admin.site.register(RespostaValidacao)


