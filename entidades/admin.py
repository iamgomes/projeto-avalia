from django.contrib import admin
from .models import Municipio, Entidade

class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ibge', 'uf']

admin.site.register(Municipio, MunicipioAdmin)


admin.site.register(Entidade)