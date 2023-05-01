from django.db import models
from .uf_choices import UfChoices


class Municipio(models.Model):
    ibge = models.CharField(max_length=7, unique=True, primary_key=True) # chave primária da tabela
    nome = models.CharField(max_length=200)
    uf = models.CharField(max_length=2, choices=UfChoices.choices)
    capital = models.BooleanField(default=False)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return '{} ({})'.format(self.nome, self.uf)
    
    def municipio_uf(self):
        return '{}-{}'.format(self.nome, self.uf)
    
    class Meta:
        ordering = ['nome']
    

class Entidade(models.Model):
    PODER_CHOICES = (
        ('D','Defensoria Pública'),
        ('E','Executivo'),
        ('J','Judiciário'),
        ('L','Legislativo'),
        ('M','Ministério Público'),
        ('T','Tribunal de Contas'),
    )

    ESFERA_CHOICES = (
        ('D','Distrital'),
        ('E','Estadual'),
        ('F','Federal'),
        ('M','Municipal'),
    )

    nome = models.CharField(max_length=200)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    poder = models.CharField(max_length=1, choices=PODER_CHOICES)
    esfera = models.CharField(max_length=1, choices=ESFERA_CHOICES)
    site = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return '{} ({})'.format(self.nome, self.municipio.uf)
    
    def entidade_uf(self):
        return '{} ({})'.format(self.nome, self.municipio.uf)