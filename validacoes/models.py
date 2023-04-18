
from django.db import models
from django.conf import settings
from django.db.models import Sum
from questionarios.models import Questionario, Resposta


class Validacao(models.Model):
    questionario = models.OneToOneField(Questionario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.questionario)
    
    @property
    def nota(self):
        return self.respostavalidacao_set.all().aggregate(Sum('nota'))['nota__sum'] or 0


class RespostaValidacao(models.Model):
    validacao = models.ForeignKey(Validacao, on_delete=models.CASCADE)
    resposta = models.OneToOneField(Resposta, on_delete=models.CASCADE)
    resposta_validacao = models.BooleanField(default=False)
    nota = models.IntegerField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.resposta_validacao)

    def save(self, *args, **kwargs):
        if self.resposta_validacao == True:
            self.nota = 10
        else:
            self.nota = 0
        return super().save(*args, **kwargs)
