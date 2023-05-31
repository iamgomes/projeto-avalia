from typing import Any
from django import forms as form
from django.contrib.auth import forms
from .models import User
from entidades.models import Municipio

class UserChangeForm(forms.UserChangeForm):

    class Meta(forms.UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'celular', 'funcao', 'municipio', 'entidade')


class UserCreationForm(forms.UserCreationForm):
    first_name = forms.forms.CharField(required=True)
    email = forms.forms.EmailField(required=True)

    class Meta(forms.UserCreationForm):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'celular', 'municipio', 'entidade', 'password1', 'password2')