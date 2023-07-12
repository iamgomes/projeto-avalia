from django.contrib import admin
from .models import Aviso

class AvisoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'aviso_texto', 'ativo', 'created_at']
    list_filter = ('ativo',)
    search_fields = ['titulo', 'aviso_texto']
admin.site.register(Aviso, AvisoAdmin)