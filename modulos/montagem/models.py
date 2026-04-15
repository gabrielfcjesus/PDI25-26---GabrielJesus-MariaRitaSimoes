"""
apps/montagem/models.py
"""
from django.db import models
from modulos.core.models import User
from modulos.producao.models import OrdemProducao


class TarefaMontagem(models.Model):
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_curso', 'Em Curso'),
        ('concluida', 'Concluída'),
        ('problema', 'Com Problema'),
    ]

    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.PROTECT, related_name='tarefas_montagem'
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendente')
    responsavel = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tarefas_montagem'
    )
    colaboradores = models.ManyToManyField(
        User, blank=True,
        related_name='tarefas_montagem_colaborador',
        verbose_name='Colaboradores na carrinha',
    )
    tempo_previsto = models.DurationField(null=True, blank=True, verbose_name='Tempo previsto')
    data_prevista = models.DateField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tarefa de Montagem'
        verbose_name_plural = 'Tarefas de Montagem'
        ordering = ['data_prevista', 'estado']

    def __str__(self):
        return f'{self.ordem} - {self.titulo}'


class RegistoMontagem(models.Model):
    """Diário de montagem no cliente"""
    tarefa = models.ForeignKey(
        TarefaMontagem, on_delete=models.CASCADE, related_name='registos'
    )
    utilizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='montagem/', null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registo de Montagem'
        verbose_name_plural = 'Registos de Montagem'
        ordering = ['-data']

    def __str__(self):
        return f'{self.tarefa} - {self.data}'
