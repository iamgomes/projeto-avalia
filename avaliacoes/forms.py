from django import forms
from questionarios.models import Tramitacao

class TramitacaoForm(forms.ModelForm):
    class Meta:
        model = Tramitacao
        #fields = '__all__'
        exclude = ['usuario','questionario']
