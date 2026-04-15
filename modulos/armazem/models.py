"""
apps/armazem/models.py
Gestão de materiais e stock
"""
from django.db import models
from modulos.core.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Material(models.Model):
    """Material em stock"""
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

    referencia = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='materiais'
    )
    descricao = models.TextField(blank=True)
    unidade = models.CharField(max_length=5, choices=UNIDADE_CHOICES, default='un')
    stock_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    localizacao = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiais'
        ordering = ['nome']

    def __str__(self):
        return f'{self.referencia} - {self.nome}'

    @property
    def stock_baixo(self):
        return self.stock_atual <= self.stock_minimo


class MovimentoStock(models.Model):
    """Entradas e saídas de stock"""
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('ajuste', 'Ajuste'),
    ]

    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, related_name='movimentos'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_posterior = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=200, blank=True)
    referencia_doc = models.CharField(max_length=100, blank=True)
    utilizador = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimento de Stock'
        verbose_name_plural = 'Movimentos de Stock'
        ordering = ['-data']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.material} ({self.quantidade})'


class PedidoCompra(models.Model):
    """Ordem de compra a fornecedor"""
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('enviado', 'Enviado ao Fornecedor'),
        ('parcialmente_recebido', 'Parcialmente Recebido'),
        ('recebido', 'Recebido'),
        ('cancelado', 'Cancelado'),
    ]

    referencia = models.CharField(max_length=30, unique=True, editable=False)
    fornecedor = models.CharField(max_length=200)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendente')
    data_pedido = models.DateField(auto_now_add=True)
    data_entrega_prevista = models.DateField(null=True, blank=True)
    data_entrega_real = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pedidos_compra')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido de Compra'
        verbose_name_plural = 'Pedidos de Compra'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.referencia} - {self.fornecedor}'

    def save(self, *args, **kwargs):
        if not self.referencia:
            from django.utils import timezone
            hoje = timezone.now().strftime('%Y%m%d')
            count = PedidoCompra.objects.filter(referencia__startswith=f'OC-{hoje}').count() + 1
            self.referencia = f'OC-{hoje}-{count:03d}'
        super().save(*args, **kwargs)

    @property
    def total_itens(self):
        return self.itens.count()

    @property
    def percentagem_recebida(self):
        itens = list(self.itens.all())
        if not itens:
            return 0
        total = sum(i.quantidade for i in itens)
        recebido = sum(i.qty_recebida for i in itens)
        if total == 0:
            return 0
        return int((recebido / total) * 100)


class ItemPedidoCompra(models.Model):
    """Linha de item de uma ordem de compra"""
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='itens')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name='itens_compra')
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    qty_recebida = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item de Pedido de Compra'
        verbose_name_plural = 'Itens de Pedido de Compra'

    def __str__(self):
        return f'{self.pedido.referencia} - {self.material.nome}'

    @property
    def por_receber(self):
        return self.quantidade - self.qty_recebida
