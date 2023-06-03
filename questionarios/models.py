from django.conf import settings
from django.db import models
from django.db.models import Sum
from entidades.models import Entidade
from avaliacoes.models import Avaliacao
from django.db.models import Q


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
    
    def qtde_essenciais(self, matriz):
        qtde = self.criterio_set.all().filter(exigibilidade='E').filter(Q(matriz='C') | Q(matriz=matriz)).count()
        va = qtde * 2
        return va
    
    def qtde_obrigatorias(self, matriz):
        qtde = self.criterio_set.all().filter(exigibilidade='O').filter(Q(matriz='C') | Q(matriz=matriz)).count()
        va = qtde * 1.5
        return va
    
    def qtde_recomendadas(self, matriz):
        qtde = self.criterio_set.all().filter(exigibilidade='R').filter(Q(matriz='C') | Q(matriz=matriz)).count()
        va = qtde * 1
        return va
    
    def va_criterio(self, matriz):
        return self.qtde_essenciais(matriz) + self.qtde_obrigatorias(matriz) + self.qtde_recomendadas(matriz)
    
    def vb_criterio(self, matriz):
        criterios_filtrados = Criterio.objects.filter(Q(matriz='C') | Q(matriz=matriz))
        dimensoes_filtradas = Dimensao.objects.filter(pk__in=[c.dimensao.id for c in criterios_filtrados])
        soma_pesos = dimensoes_filtradas.aggregate(Sum("peso"))['peso__sum']
        peso_normalizado = self.peso / soma_pesos * 100
        total = peso_normalizado / self.va_criterio(matriz)
        return total
    
    def vn_essenciais(self, matriz):
        total = self.vb_criterio(matriz) * 2
        return total
    
    def vn_obrigatorias(self, matriz):
        total = self.vb_criterio(matriz) * 1.5
        return total
    
    def vn_recomendadas(self, matriz):
        return self.vb_criterio(matriz) * 1
    

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
        ('I','Administração Indireta')
    )

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    dimensao = models.ForeignKey(Dimensao, on_delete=models.CASCADE)
    cod = models.IntegerField()
    criterio_texto = models.CharField(max_length=500)
    itens_avaliacao = models.ManyToManyField(ItemAvaliacao, through='CriterioItem')
    exigibilidade = models.CharField(max_length=1, choices=EXIGIBILIDADE_CHOICES)
    matriz = models.CharField(max_length=1, choices=MATRIZ_CHOICES)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ('cod', )

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
        return self.avaliacao.criterio_set.all().filter(Q(matriz='C') | Q(matriz=self.entidade.poder)).count()
    
    @property
    def total_criterios_essenciais(self):
        return self.avaliacao.criterio_set.filter(exigibilidade='E').filter(Q(matriz='C') | Q(matriz=self.entidade.poder)).count()
    
    @property
    def total_criterios_essenciais_atendidos(self):
        return self.resposta_set.filter(resposta=True).filter(criterio_item__criterio__exigibilidade='E').filter(criterio_item__item_avaliacao=1).count() or 0
    
    @property
    def percentual_atendido_essenciais(self):
        total = self.total_criterios_essenciais_atendidos / self.total_criterios_essenciais * 100
        return round(total, 2)
    
    @property
    def classificacao(self):
        try:
            if self.percentual_atendido_essenciais == 100:
                if self.nota >= 95:
                    nivel = 'Diamante'
                if self.nota >= 85 and self.nota < 95:
                    nivel = 'Ouro'
                if self.nota >= 75 and self.nota < 85:
                    nivel = 'Prata'
            else:
                if self.nota >= 75:
                    nivel = 'Elevado'
                if self.nota >= 50 and self.nota < 75:
                    nivel = 'Intermediário'
                if self.nota >= 30 and self.nota < 50:
                    nivel = 'Básico'
                if self.nota >= 1 and self.nota < 30:
                    nivel = 'Inicial'
                if self.nota < 1:
                    nivel = 'Inexistente'
        except:
            nivel = 'Inexistente'

        return nivel
    

class Resposta(models.Model):
    questionario = models.ForeignKey(Questionario, on_delete=models.CASCADE)
    criterio_item = models.ForeignKey(CriterioItem, on_delete=models.CASCADE)
    resposta = models.BooleanField(default=False)
    nota = models.FloatField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.resposta)
    

    def total_item(self):
        if self.criterio_item.criterio.exigibilidade == 'E':
            valor_item = self.criterio_item.criterio.dimensao.vn_essenciais(self.questionario.entidade.poder)
        if self.criterio_item.criterio.exigibilidade == 'O':
            valor_item = self.criterio_item.criterio.dimensao.vn_obrigatorias(self.questionario.entidade.poder)
        if self.criterio_item.criterio.exigibilidade == 'R':
            valor_item = self.criterio_item.criterio.dimensao.vn_recomendadas(self.questionario.entidade.poder)

        total = valor_item / self.criterio_item.criterio.soma_pesos_aplicaveis * self.criterio_item.item_avaliacao.peso

        return total

    
    def save(self, *args, **kwargs):
        if self.resposta == True:
            self.nota = self.total_item()
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