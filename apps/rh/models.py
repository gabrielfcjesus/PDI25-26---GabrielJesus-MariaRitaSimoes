"""
apps/rh/models.py
Gestão de trabalhadores e informações de RH
"""
from django.db import models
from apps.core.models import User, Departamento, Cargo


class Trabalhador(models.Model):
    """Registo de trabalhador (pode ou não ter conta de utilizador)"""
    ESTADO_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('ferias', 'De Férias'),
        ('baixa', 'De Baixa'),
    ]

    TIPO_CONTRATO = [
        ('efetivo', 'Efetivo'),
        ('termo_certo', 'A Termo Certo'),
        ('termo_incerto', 'A Termo Incerto'),
        ('estagio', 'Estágio'),
        ('recibos_verdes', 'Recibos Verdes'),
    ]

    # Dados pessoais
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    nif = models.CharField(max_length=9, unique=True, verbose_name='NIF')
    data_nascimento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='trabalhadores/', null=True, blank=True)

    # Dados profissionais
    departamento = models.ForeignKey(
        Departamento, on_delete=models.PROTECT, related_name='trabalhadores'
    )
    cargo = models.ForeignKey(
        Cargo, on_delete=models.PROTECT, related_name='trabalhadores'
    )
    data_admissao = models.DateField()
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO, default='efetivo')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ativo')

    # Ligação opcional a conta de utilizador
    utilizador = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='trabalhador'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Trabalhador'
        verbose_name_plural = 'Trabalhadores'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class AusenciaFalta(models.Model):
    """Registo de ausências e faltas"""
    TIPO_CHOICES = [
        ('ferias', 'Férias'),
        ('falta_justificada', 'Falta Justificada'),
        ('falta_injustificada', 'Falta Injustificada'),
        ('baixa_medica', 'Baixa Médica'),
        ('licenca', 'Licença'),
    ]

    trabalhador = models.ForeignKey(
        Trabalhador, on_delete=models.CASCADE, related_name='ausencias'
    )
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    observacoes = models.TextField(blank=True)
    aprovado = models.BooleanField(default=False)
    aprovado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Ausência / Falta'
        verbose_name_plural = 'Ausências / Faltas'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'{self.trabalhador} - {self.get_tipo_display()} ({self.data_inicio})'
