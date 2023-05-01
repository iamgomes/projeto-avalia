from django.db import models


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
    data_inicial = models.DateTimeField(null=True, blank=True)
    data_final = models.DateTimeField(null=True, blank=True)
    data_inicial_validacao= models.DateTimeField(null=True, blank=True)
    data_final_validacao = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.titulo
    

