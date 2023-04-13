from django.forms import ModelForm
from . models import Resposta

class RespostaForm(ModelForm):
    class Meta:
        model = Resposta
        #fields = '__all__'
        exclude = ['usuarioavaliacao', 'criterio']
