from django.contrib import admin
from .models import User
from django.contrib.auth import admin as admin_auth_django
from .forms import UserChangeForm, UserCreationForm


@admin.register(User)
class UserAdmin(admin_auth_django.UserAdmin):
    form = UserChangeForm
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'municipio']
    fieldsets = admin_auth_django.UserAdmin.fieldsets + (
        ('Função e Setor', {'fields':('funcao','setor')}),
        ('Município', {'fields':('municipio','entidade',)}),
        ('Foto e Celular', {'fields':('foto','celular')}),
    )
