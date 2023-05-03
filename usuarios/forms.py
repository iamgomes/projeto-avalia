from django import forms 
from django.contrib.auth import forms
from .models import User

class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User
        fields = '__all__'


class UserCreationForm(forms.UserCreationForm):
    first_name = forms.forms.CharField(required=True)
    email = forms.forms.EmailField(required=True)

    class Meta(forms.UserCreationForm):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'celular', 'municipio', 'entidade', 'password1', 'password2')