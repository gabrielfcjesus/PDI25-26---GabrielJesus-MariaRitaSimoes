"""
apps/auditoria/models.py
Registo de auditoria e rastreabilidade de ações no sistema.
"""
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from modulos.core.models import User


class AuditLog(models.Model):
    ACAO_CHOICES = [
        # Autenticação
        ('login', 'Login'),
        ('login_falhado', 'Login Falhado'),
        ('logout', 'Logout'),
        # CRUD
        ('criacao', 'Criação'),
        ('edicao', 'Edição'),
        ('eliminacao', 'Eliminação'),
        # Operações de negócio
        ('mudanca_estado', 'Mudança de Estado'),
        ('mudanca_permissao', 'Mudança de Permissão'),
        ('movimento_stock', 'Movimento de Stock'),
        ('acao_admin', 'Ação Administrativa'),
        # Segurança / erros
        ('acesso_negado', 'Acesso Negado'),
        ('erro', 'Erro'),
        ('outro', 'Outro'),
    ]

    # Quem
    utilizador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs'
    )
    # Preserva o username mesmo que o utilizador seja eliminado
    username_cache = models.CharField(max_length=150, blank=True)

    # O quê
    acao = models.CharField(max_length=25, choices=ACAO_CHOICES, db_index=True)
    modulo = models.CharField(max_length=50, blank=True, db_index=True)
    descricao = models.TextField(blank=True)

    # Quando
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Onde / como
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    endpoint = models.CharField(max_length=300, blank=True)
    metodo_http = models.CharField(max_length=10, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)

    # Dados antes/depois (campos sensíveis já mascarados pelo serviço)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)

    # Informação adicional livre
    extra = models.JSONField(null=True, blank=True)

    # Associação genérica a qualquer entidade do sistema
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.CharField(max_length=50, blank=True)
    objeto = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['utilizador', '-timestamp']),
            models.Index(fields=['acao', '-timestamp']),
            models.Index(fields=['modulo', '-timestamp']),
        ]

    def __str__(self):
        user = self.username_cache or '(anónimo)'
        return f'[{self.timestamp:%d/%m/%Y %H:%M}] {user} — {self.get_acao_display()} — {self.modulo}'
