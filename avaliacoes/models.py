from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from entidades.models import Entidade


class GrupoAvaliacao(models.Model):
    titulo = models.CharField(max_length=50)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.titulo
    

class Avaliacao(models.Model):
    ano_exercicio = models.IntegerField()
    grupo = models.ForeignKey(GrupoAvaliacao, on_delete=models.SET_NULL, null=True)
    titulo = models.CharField(max_length=50)
    descricao = models.TextField(null=True,blank=True)
    data_inicial = models.DateField(null=True, blank=True)
    data_final = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.titulo
    

class Dimensao(models.Model):
    dimensao_texto = models.CharField(max_length=100)
    peso = models.IntegerField()
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.dimensao_texto
    

class GrupoCriterio(models.Model):
    titulo = models.CharField(max_length=50)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.titulo
    

class Criterio(models.Model):
    EXIGIBILIDADE_CHOICES = (
        ('E','Essencial'),
        ('O','Obrigatório'),
        ('R','Recomendado'),
    )

    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoCriterio, on_delete=models.CASCADE)
    criterio_texto = models.CharField(max_length=200)
    dimensoes = models.ManyToManyField(Dimensao, through='CriterioDimensao')
    exigibilidade = models.CharField(max_length=1, choices=EXIGIBILIDADE_CHOICES)
    descricao = models.TextField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.criterio_texto


class UsuarioAvaliacao(models.Model):
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
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
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


class UsuarioAvaliacaoValidacao(models.Model):
    usuario_avaliacao = models.OneToOneField(UsuarioAvaliacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.usuario_avaliacao)
    
    @property
    def nota(self):
        return self.respostavalidacao_set.all().aggregate(Sum('nota'))['nota__sum'] or 0


class CriterioDimensao(models.Model):
    criterio = models.ForeignKey(Criterio, on_delete=models.CASCADE)
    dimensao = models.ForeignKey(Dimensao, on_delete=models.CASCADE)

    def __str__(self):
        return '{}/{}'.format(self.criterio, self.dimensao)
    
    class Meta:
        unique_together = ['criterio', 'dimensao']


class Resposta(models.Model):
    RESPOSTA_CHOICES = (
        ('A','Atende'),
        ('N','Não Atende'),
        ('P','Parcialmente'),
    )

    usuarioavaliacao = models.ForeignKey(UsuarioAvaliacao, on_delete=models.CASCADE)
    criterio_dimensao = models.ForeignKey(CriterioDimensao, on_delete=models.CASCADE)
    resposta = models.CharField(max_length=1, choices=RESPOSTA_CHOICES)
    nota = models.IntegerField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.get_resposta_display()
    
    def save(self, *args, **kwargs):
        if self.resposta == 'A':
            self.nota = 10
        elif self.resposta == 'P':
            self.nota = 5
        else:
            self.nota = 0
        return super().save(*args, **kwargs)
    

class ImagemEvidencia(models.Model):
    resposta = models.ForeignKey(Resposta, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='imagem_evidencia')
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)



class RespostaValidacao(models.Model):
    RESPOSTA_CHOICES = (
        ('A','Atende'),
        ('N','Não Atende'),
        ('P','Parcialmente'),
    )

    usuario_avaliacao_validacao = models.ForeignKey(UsuarioAvaliacaoValidacao, on_delete=models.CASCADE)
    resposta = models.OneToOneField(Resposta, on_delete=models.CASCADE)
    resposta_validacao = models.CharField(max_length=1, choices=RESPOSTA_CHOICES)
    nota = models.IntegerField(null=True,blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.get_resposta_validacao_display()

    def save(self, *args, **kwargs):
        if self.resposta_validacao == 'A':
            self.nota = 10
        elif self.resposta_validacao == 'P':
            self.nota = 5
        else:
            self.nota = 0
        return super().save(*args, **kwargs)
