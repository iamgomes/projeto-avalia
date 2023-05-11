from django.conf import settings
from django.db import models
from django.db.models import Sum
from entidades.models import Entidade
from avaliacoes.models import Avaliacao



#Antiga tabela Dimensao
class ItemAvaliacao(models.Model):
    item_avaliacao = models.CharField(max_length=100)
    peso = models.IntegerField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.item_avaliacao
    

#Antiga tabela GrupoCriterio
class Dimensao(models.Model):
    dimensao_texto = models.CharField(max_length=50)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.dimensao_texto
    

class Criterio(models.Model):
    EXIGIBILIDADE_CHOICES = (
        ('E','Essencial'),
        ('O','Obrigatório'),
        ('R','Recomendado'),
    )

    MATRIZ_CHOICES = (
        ('C','Comum'),
        ('E','Executivo'),
        ('L','Legislativo'),
        ('J','Judiciário'),
        ('T','Tribunal de Contas'),
        ('M','Ministério Púbico'),
        ('D','Defensoria Pública'),
    )

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    dimensao = models.ForeignKey(Dimensao, on_delete=models.CASCADE)
    cod = models.CharField(max_length=10)
    criterio_texto = models.CharField(max_length=200)
    itens_avaliacao = models.ManyToManyField(ItemAvaliacao, through='CriterioItem')
    exigibilidade = models.CharField(max_length=1, choices=EXIGIBILIDADE_CHOICES)
    matriz = models.CharField(max_length=1, choices=MATRIZ_CHOICES)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.criterio_texto


class CriterioItem(models.Model):
    criterio = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    item_avaliacao = models.ForeignKey(ItemAvaliacao, on_delete=models.CASCADE)

    def __str__(self):
        return '{}/{}'.format(self.criterio, self.item_avaliacao)
    
    class Meta:
        unique_together = ['criterio', 'item_avaliacao']


#Antiga tabela UsuarioAvaliacao
class Questionario(models.Model):
    STATUS_CHOICES = (
        ('NS','Não possui site'),
        ('I','Iniciado'),
        ('F','Finalizado'),
        ('E','Editando'),
        ('A','Aguardando Validação'),
        ('EV','Em Validação'),
        ('V','Validado'),
        ('ER','Em Revisão'),
    )

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='I')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        unique_together = ['avaliacao', 'entidade']
        ordering = ('-created_at', )

    def __str__(self):
        return f'{self.usuario}/{self.entidade}'
    
    @property
    def nota(self):
        return self.resposta_set.all().aggregate(Sum('nota'))['nota__sum'] or 0
    
    @property
    def total_criterios(self):
        return self.avaliacao.criterio_set.all().count()
    
    @property
    def total_criterios_respondidos(self):
        return self.resposta_set.exclude(resposta__exact='').values('criterio_dimensao__criterio').distinct().count()


class Resposta(models.Model):
    questionario = models.ForeignKey(Questionario, on_delete=models.CASCADE)
    criterio_item = models.ForeignKey(CriterioItem, on_delete=models.CASCADE)
    resposta = models.BooleanField(default=False)
    nota = models.IntegerField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.resposta)
    
    def save(self, *args, **kwargs):
        if self.resposta == True:
            self.nota = 10
        else:
            self.nota = 0
        return super().save(*args, **kwargs)
    

class LinkEvidencia(models.Model):
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE)
    link = models.TextField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)
    

class ImagemEvidencia(models.Model):
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE)
    imagem = models.FileField(upload_to='imagem_evidencia')
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)


class JustificativaEvidencia(models.Model):
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE)
    justificativa = models.TextField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.justificativa)


class Tramitacao(models.Model):
    SETOR_CHOICES = (
        ('C', 'Controle Interno'),
        ('T', 'Tribunal de Contas'),
        ('A', 'Atricon')
    )

    MOTIVO_CHOICES = (
        #Controle Interno
        ('C', (
            ('AI', 'Andamento Iniciado'),
            ('PC', 'Envio Para Revisão da Avaliação'),
        )),

        #Tribunal
        ('T', (
            ('IT', 'Andamento Iniciado pelo Tribunal'),
            ('EA', 'Envio para Análise do Tribunal'),
            ('RT', 'Envio para Revisão do Tribunal'),
        )),
        #Atricon
        ('A', (
            ('EC', 'Envio para Conclusão'),
        )),
    )
    questionario = models.ForeignKey(Questionario, on_delete=models.CASCADE)
    setor = models.CharField(max_length=1, choices=SETOR_CHOICES)
    motivo = models.CharField(max_length=2, choices=MOTIVO_CHOICES)
    observacao = models.TextField(null=True,blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.get_motivo_display()

    class Meta:
        ordering = ('-created_at', )