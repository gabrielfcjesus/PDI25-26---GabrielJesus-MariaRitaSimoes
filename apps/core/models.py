"""
apps/core/models.py
Modelos base: User personalizado, Departamento, Cargo
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Departamento(models.Model):
    """Departamentos da empresa"""
    DEPARTAMENTOS = [
        ('direcao', 'Direção / Administração'),
        ('rh', 'Recursos Humanos'),
        ('armazem', 'Armazém'),
        ('planeamento', 'Planeamento'),
        ('producao', 'Produção'),
        ('qualidade', 'Controlo de Qualidade'),
        ('expedicao', 'Expedição'),
        ('montagem', 'Montagem'),
    ]

    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True, choices=DEPARTAMENTOS)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Cargo(models.Model):
    """Cargos dentro de cada departamento"""
    nome = models.CharField(max_length=100)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name='cargos'
    )
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['departamento', 'nome']

    def __str__(self):
        return f'{self.nome} ({self.departamento})'


class User(AbstractUser):
    """
    Utilizador personalizado com departamento, cargo e permissões ERP.
    Substitui o User padrão do Django (AUTH_USER_MODEL = 'core.User').
    """
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='utilizadores'
    )
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='utilizadores'
    )
    telefone = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='utilizadores/', null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'

    def __str__(self):
        return f'{self.get_full_name() or self.username}'

    @property
    def is_direcao(self):
        return self.is_superuser or (
            self.departamento and self.departamento.codigo == 'direcao'
        )

    @property
    def codigo_departamento(self):
        if self.departamento:
            return self.departamento.codigo
        return None

    def tem_acesso(self, modulo):
        """Verifica se o utilizador tem acesso a um módulo específico"""
        if self.is_direcao:
            return True
        return self.codigo_departamento == modulo
