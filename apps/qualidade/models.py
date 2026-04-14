"""
apps/qualidade/models.py
"""
from django.db import models
from apps.core.models import User
from apps.producao.models import OrdemProducao


class InspecaoQualidade(models.Model):
    RESULTADO_CHOICES = [
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('aprovado_condicional', 'Aprovado Condicionalmente'),
    ]

    TIPO_CHOICES = [
        ('intermedia', 'Intermédia'),
        ('final', 'Final'),
    ]

    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.PROTECT, related_name='inspecoes'
    )
    inspector = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='inspecoes'
    )
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES, default='final')
    data = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=25, choices=RESULTADO_CHOICES)
    observacoes = models.TextField(blank=True)
    nao_conformidades = models.TextField(blank=True, verbose_name='Não Conformidades')
    acoes_corretivas = models.TextField(blank=True, verbose_name='Ações Corretivas')

    class Meta:
        verbose_name = 'Inspeção de Qualidade'
        verbose_name_plural = 'Inspeções de Qualidade'
        ordering = ['-data']

    def __str__(self):
        return f'Inspeção {self.ordem} - {self.get_resultado_display()}'
