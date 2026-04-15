"""
apps/planeamento/models.py
Planeamento — clientes da empresa
"""
from django.db import models


class Cliente(models.Model):
    """Clientes da empresa"""
    nome = models.CharField(max_length=200)
    nif = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    morada = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome
