from django.contrib import admin
from .models import User
from django.contrib.auth import admin as admin_auth_django
from .forms import UserChangeForm, UserCreationForm

@admin.register(User)
class UserAdmin(admin_auth_django.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    fieldsets = admin_auth_django.UserAdmin.fieldsets + (
        ('Função', {'fields':('funcao',)}),
        ('Município', {'fields':('municipio', 'entidade',)}),
        ('Foto', {'fields':('foto',)}),
    )
