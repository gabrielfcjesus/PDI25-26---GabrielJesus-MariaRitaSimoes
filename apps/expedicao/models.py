"""
apps/expedicao/models.py
"""
from django.db import models
from apps.core.models import User
from apps.producao.models import OrdemProducao


class Veiculo(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['matricula']

    def __str__(self):
        return f'{self.matricula} — {self.descricao}'


class Expedicao(models.Model):
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_preparacao', 'Em Preparação'),
        ('pronta', 'Pronta para Envio'),
        ('enviada', 'Enviada'),
        ('entregue', 'Entregue'),
    ]

    referencia = models.CharField(max_length=30, unique=True)
    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.PROTECT, related_name='expedicoes'
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendente')
    data_prevista_envio = models.DateField(null=True, blank=True)
    data_real_envio = models.DateTimeField(null=True, blank=True)
    transportadora = models.CharField(max_length=100, blank=True)
    guia_transporte = models.CharField(max_length=100, blank=True)
    morada_entrega = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    responsavel = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='expedicoes'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Expedição'
        verbose_name_plural = 'Expedições'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.referencia} - {self.ordem}'
