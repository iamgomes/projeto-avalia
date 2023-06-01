from django.contrib import admin
from .models import Avaliacao, GrupoAvaliacao


class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ano_exercicio', 'grupo', 'data_inicial', 'data_final']
admin.site.register(Avaliacao, AvaliacaoAdmin)

admin.site.register(GrupoAvaliacao)