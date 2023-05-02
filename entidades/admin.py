from django.contrib import admin
from .models import Municipio, Entidade

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ibge', 'uf', 'capital']
    list_filter = ('uf', 'capital')
    search_fields = ('nome',)

admin.site.register(Municipio, MunicipioAdmin)


class EntidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'municipio', 'poder', 'esfera']
    list_filter = ('poder','esfera')

admin.site.register(Entidade, EntidadeAdmin)