from django.db import models


class Aviso(models.Model):
    titulo = models.CharField(max_length=50)
    aviso_texto = models.TextField(null=True,blank=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateField(auto_now=False, auto_now_add=True)
    updated_at = models.DateField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo
