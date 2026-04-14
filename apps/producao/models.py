"""
apps/producao/models.py
Ordens de Produção e acompanhamento do fabrico
"""
from django.db import models
from apps.core.models import User
from apps.planeamento.models import Cliente
from apps.armazem.models import Material


class OrdemProducao(models.Model):
    """Ordem de Produção (OP) — cobre todo o ciclo de vida da encomenda"""
    ESTADO_CHOICES = [
        ('planeamento', 'Em Planeamento'),
        ('em_producao', 'Em Produção'),
        ('pausada', 'Pausada'),
        ('qualidade', 'Em Controlo de Qualidade'),
        ('expedicao', 'Em Expedição'),
        ('montagem', 'Em Montagem'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    # Identificação
    referencia = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=200)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name='ordens'
    )
    descricao = models.TextField(blank=True)

    # Estado e prioridade
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='planeamento')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='normal')

    # Datas
    data_entrega_prevista = models.DateField(null=True, blank=True)
    data_entrega_real = models.DateField(null=True, blank=True)
    data_prevista_inicio = models.DateField(null=True, blank=True)
    data_prevista_fim = models.DateField(null=True, blank=True)
    data_real_inicio = models.DateTimeField(null=True, blank=True)
    data_real_fim = models.DateTimeField(null=True, blank=True)
    data_planeamento = models.DateTimeField(null=True, blank=True, verbose_name='Data/Hora de Planeamento')

    responsavel = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ops_responsavel'
    )
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='ops_criadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordem de Produção'
        verbose_name_plural = 'Ordens de Produção'
        ordering = ['-data_entrega_prevista', '-criado_em']

    def __str__(self):
        return f'{self.referencia} - {self.nome}'


class FicheiroTecnico(models.Model):
    ordem = models.ForeignKey(OrdemProducao, on_delete=models.CASCADE, related_name='ficheiros')
    ficheiro = models.FileField(upload_to='tecnicos/')
    nome = models.CharField(max_length=200, blank=True)
    carregado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['carregado_em']

    def __str__(self):
        return self.nome or self.ficheiro.name


class ItemProducao(models.Model):
    """Item/componente dentro de uma OP"""
    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.CASCADE, related_name='itens'
    )
    descricao = models.CharField(max_length=200)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, blank=True
    )
    concluido = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Item de Produção'
        verbose_name_plural = 'Itens de Produção'

    def __str__(self):
        return f'{self.descricao} ({self.quantidade})'


class RegistoProducao(models.Model):
    """Registo de atividade na produção"""
    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.CASCADE, related_name='registos'
    )
    utilizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registo de Produção'
        verbose_name_plural = 'Registos de Produção'
        ordering = ['-data']

    def __str__(self):
        return f'{self.ordem} - {self.data}'


class PedidoMaterialAdicional(models.Model):
    """Pedido de material adicional feito durante a produção de uma OP.

    Garante rastreabilidade do material extra consumido: quem pediu, porquê,
    quanto foi entregue e qual a saída de stock gerada.
    """
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_preparacao', 'Em Preparação'),
        ('entregue', 'Entregue'),
        ('parcialmente_entregue', 'Parcialmente Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    UNIDADE_CHOICES = [
        ('un', 'Unidade'),
        ('kg', 'Quilograma'),
        ('m', 'Metro'),
        ('m2', 'Metro Quadrado'),
        ('m3', 'Metro Cúbico'),
        ('l', 'Litro'),
        ('caixa', 'Caixa'),
        ('rolo', 'Rolo'),
    ]

    # Associação obrigatória à OP — nunca existe sem ela
    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.PROTECT, related_name='pedidos_material'
    )

    # Material do armazém (opcional — pode ser descrição livre se ainda não estiver catalogado)
    material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pedidos_producao'
    )
    descricao_material = models.CharField(max_length=200, verbose_name='Material / Descrição')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade = models.CharField(max_length=10, choices=UNIDADE_CHOICES, default='un')

    # Justificação obrigatória para garantir rastreabilidade
    justificacao = models.TextField(verbose_name='Justificação')
    observacoes = models.TextField(blank=True)

    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='pendente')

    # Quem pediu e quando
    pedido_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='pedidos_material_criados'
    )
    pedido_em = models.DateTimeField(auto_now_add=True)

    # Quem processou/entregou e quando
    processado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pedidos_material_processados'
    )
    processado_em = models.DateTimeField(null=True, blank=True)
    quantidade_entregue = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Pedido de Material Adicional'
        verbose_name_plural = 'Pedidos de Material Adicional'
        ordering = ['-pedido_em']

    def __str__(self):
        return f'{self.descricao_material} ({self.quantidade} {self.unidade}) — OP {self.ordem.referencia}'


class PedidoAssistencia(models.Model):
    """Pedido de assistencia enviado pela producao para planeamento/direcao."""
    URGENCIA_CHOICES = [
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Analise'),
        ('resolvido', 'Resolvido'),
    ]

    ordem = models.ForeignKey(
        OrdemProducao, on_delete=models.CASCADE, related_name='pedidos_assistencia'
    )
    descricao = models.TextField(verbose_name='Descricao do problema')
    urgencia = models.CharField(max_length=10, choices=URGENCIA_CHOICES, default='normal')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendente')

    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assistencias_criadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    resposta = models.TextField(blank=True)
    respondido_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assistencias_respondidas'
    )
    respondido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Pedido de Assistencia'
        verbose_name_plural = 'Pedidos de Assistencia'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Assistencia OP {self.ordem.referencia} — {self.get_urgencia_display()}'
