from django.conf import settings
from django.db import models
from django.db.models import Sum
from entidades.models import Entidade
from avaliacoes.models import Avaliacao
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    peso = models.IntegerField(default=1)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.dimensao_texto
    
    # VA = Valor Absoluto, VB = Valor Base, VN = Valor Normalizado
    
    @property
    def qtde_essenciais(self):
        return self.criterio_set.all().filter(exigibilidade='E').count()
    
    @property
    def va_essenciais(self):
        total = self.qtde_essenciais * 2
        return total
    
    @property
    def qtde_obrigatorias(self):
        return self.criterio_set.all().filter(exigibilidade='O').count()
    
    @property
    def va_obrigatorias(self):
        total = self.qtde_obrigatorias * 1.5
        return total
    
    @property
    def qtde_recomendadas(self):
        return self.criterio_set.all().filter(exigibilidade='R').count()
    
    @property
    def va_recomendadas(self):
        return self.qtde_recomendadas * 1
    
    @property
    def va_criterio(self):
        return self.va_essenciais + self.va_obrigatorias + self.va_recomendadas
    
    @property
    def soma_pesos(self):
        return Dimensao.objects.aggregate(Sum("peso"))['peso__sum'] #37
    
    @property
    def peso_normalizado(self):
        total = self.peso / self.soma_pesos * 100
        return total
    
    @property
    def vb_criterio(self):
        total = self.peso_normalizado / self.va_criterio
        return total
    
    @property
    def vn_essenciais(self):
        total = self.vb_criterio * 2
        return total
    
    @property
    def vn_obrigatorias(self):
        total = self.vb_criterio * 1.5
        return total
    
    @property
    def vn_recomendadas(self):
        return self.vb_criterio * 1
    

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
    criterio_texto = models.CharField(max_length=500)
    itens_avaliacao = models.ManyToManyField(ItemAvaliacao, through='CriterioItem')
    exigibilidade = models.CharField(max_length=1, choices=EXIGIBILIDADE_CHOICES)
    matriz = models.CharField(max_length=1, choices=MATRIZ_CHOICES)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return '{} {}'.format(self.cod, self.criterio_texto)
    
    #Soma dos pesos do itens aplicáveis ao critério
    @property
    def soma_pesos_aplicaveis(self):
        return self.itens_avaliacao.aggregate(Sum("peso"))['peso__sum']


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
        ('I','Iniciado'),
        ('E','Editando'),
        ('F','Finalizado UG'),
        ('AV','Aguardando Validação'),
        ('EV','Em Validação'),
        ('V','Validado'),
    )

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='I')
    indice = models.FloatField(default=0)
    nivel = models.CharField(max_length=50, default='Inexistente')
    essenciais = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        unique_together = ['avaliacao', 'entidade']
        ordering = ('-created_at', )

    def __str__(self):
        return f'{self.usuario}/{self.entidade}'
    
    @property
    def nota(self):
        total = self.resposta_set.all().aggregate(Sum('nota'))['nota__sum'] or 0
        return round(total, 2)
    
    @property
    def total_criterios(self):
        return self.avaliacao.criterio_set.all().count()
    
    @property
    def total_criterios_essenciais(self):
        return self.avaliacao.criterio_set.filter(exigibilidade='E').count()
    
    @property
    def total_criterios_essenciais_atendidos(self):
        return self.resposta_set.filter(resposta=True).filter(criterio_item__criterio__exigibilidade='E').count() or 0
    
    @property
    def percentual_atendido_essenciais(self):
        total = self.total_criterios_essenciais_atendidos / self.total_criterios_essenciais * 100
        return total
    
    @property
    def classificacao(self):
        if self.percentual_atendido_essenciais == 100:
            if self.nota >= 95:
                nivel_t = 'Diamante'
            if self.nota >= 85 and self.nota < 95:
                nivel_t = 'Ouro'
            if self.nota >= 75 and self.nota < 85:
                nivel_t = 'Prata'
        else:
            if self.nota >= 75:
                nivel_t = 'Elevado'
            if self.nota >= 50 and self.nota < 75:
                nivel_t = 'Intermediário'
            if self.nota >= 30 and self.nota < 50:
                nivel_t = 'Básico'
            if self.nota >= 1 and self.nota < 30:
                nivel_t = 'Inicial'
            if self.nota < 1:
                nivel_t = 'Inexistente'

        return nivel_t
    

class Resposta(models.Model):
    questionario = models.ForeignKey(Questionario, on_delete=models.CASCADE)
    criterio_item = models.ForeignKey(CriterioItem, on_delete=models.CASCADE)
    resposta = models.BooleanField(default=False)
    nota = models.FloatField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.resposta)
    
    @property
    def total_item(self):
        if self.criterio_item.criterio.exigibilidade == 'E':
            valor_item = self.criterio_item.criterio.dimensao.vn_essenciais
        if self.criterio_item.criterio.exigibilidade == 'O':
            valor_item = self.criterio_item.criterio.dimensao.vn_obrigatorias
        if self.criterio_item.criterio.exigibilidade == 'R':
            valor_item = self.criterio_item.criterio.dimensao.vn_recomendadas

        total = valor_item / self.criterio_item.criterio.soma_pesos_aplicaveis * self.criterio_item.item_avaliacao.peso

        return total

    
    def save(self, *args, **kwargs):
        if self.resposta == True:
            self.nota = self.total_item
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


@receiver(post_save, sender=Questionario)
def update_indice(sender, instance, created, **kwargs):
    indice = instance.nota
    nivel = instance.classificacao
    essenciais = instance.percentual_atendido_essenciais
    Questionario.objects.filter(pk=instance.id).update(indice=indice, nivel=nivel, essenciais=essenciais)