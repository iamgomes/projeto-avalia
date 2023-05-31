
from django.db import models
from django.conf import settings
from django.db.models import Sum
from questionarios.models import Questionario, Resposta, CriterioItem
from django.db.models.signals import post_save
from django.dispatch import receiver


class Validacao(models.Model):
    questionario = models.OneToOneField(Questionario, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    indice = models.FloatField(default=0)
    nivel = models.CharField(max_length=50, default='Inexistente')
    essenciais = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return str(self.questionario)
    
    @property
    def nota(self):
        total = self.respostavalidacao_set.all().aggregate(Sum('nota'))['nota__sum'] or 0
        return round(total, 2)
    
    @property
    def total_criterios_essenciais_atendidos(self):
        return self.respostavalidacao_set.filter(resposta_validacao=True).filter(resposta__criterio_item__criterio__exigibilidade='E').count()
    
    @property
    def percentual_atendido_essenciais(self):
        total = self.total_criterios_essenciais_atendidos / self.questionario.total_criterios_essenciais * 100
        return total
    
    @property
    def classificacao_validacao(self):
        if self.percentual_atendido_essenciais == 100:
            if self.nota >= 95:
                nivel_tv = 'Diamante'
            if self.nota >= 85 and self.nota < 95:
                nivel_tv = 'Ouro'
            if self.nota >= 75 and self.nota < 85:
                nivel_tv = 'Prata'
        else:
            if self.nota >= 75:
                nivel_tv = 'Elevado'
            if self.nota >= 50 and self.nota < 75:
                nivel_tv = 'Intermediário'
            if self.nota >= 30 and self.nota < 50:
                nivel_tv = 'Básico'
            if self.nota >= 1 and self.nota < 30:
                nivel_tv = 'Inicial'
            if self.nota < 1:
                nivel_tv = 'Inexistente'

        return nivel_tv


class RespostaValidacao(models.Model):
    validacao = models.ForeignKey(Validacao, on_delete=models.CASCADE)
    criterio_item = models.ForeignKey(CriterioItem, on_delete=models.CASCADE)
    resposta = models.OneToOneField(Resposta, on_delete=models.CASCADE)
    resposta_validacao = models.BooleanField(default=False)
    nota = models.FloatField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.resposta_validacao)
    
    @property
    def total_item_validacao(self):
        if self.resposta.criterio_item.criterio.exigibilidade == 'E':
            valor_item = self.resposta.criterio_item.criterio.dimensao.vn_essenciais
        if self.resposta.criterio_item.criterio.exigibilidade == 'O':
            valor_item = self.resposta.criterio_item.criterio.dimensao.vn_obrigatorias
        if self.resposta.criterio_item.criterio.exigibilidade == 'R':
            valor_item = self.resposta.criterio_item.criterio.dimensao.vn_recomendadas

        total = valor_item / self.resposta.criterio_item.criterio.soma_pesos_aplicaveis * self.resposta.criterio_item.item_avaliacao.peso

        return total

    def save(self, *args, **kwargs):
        if self.resposta_validacao == True:
            self.nota = self.total_item_validacao
        else:
            self.nota = 0
        return super().save(*args, **kwargs)
    

class LinkEvidenciaValidacao(models.Model):
    resposta_validacao = models.ForeignKey(RespostaValidacao, on_delete=models.CASCADE)
    link_validacao = models.TextField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)
    

class ImagemEvidenciaValidacao(models.Model):
    resposta_validacao = models.ForeignKey(RespostaValidacao, on_delete=models.CASCADE)
    imagem_validacao = models.FileField(upload_to='imagem_evidencia_validacao')
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)


class JustificativaEvidenciaValidacao(models.Model):
    resposta_validacao = models.ForeignKey(RespostaValidacao, on_delete=models.CASCADE)
    justificativa_validacao = models.TextField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.justificativa_validacao)


@receiver(post_save, sender=Validacao)
def update_indice_validacao(sender, instance, created, **kwargs):
    if created:
        print('Foi criado alguma coisa')
    else:
        print('Nada a declarar')