from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('producao', '0001_initial'),
        ('armazem', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoMaterialAdicional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao_material', models.CharField(max_length=200, verbose_name='Material / Descrição')),
                ('quantidade', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unidade', models.CharField(
                    choices=[
                        ('un', 'Unidade'), ('kg', 'Quilograma'), ('m', 'Metro'),
                        ('m2', 'Metro Quadrado'), ('m3', 'Metro Cúbico'),
                        ('l', 'Litro'), ('caixa', 'Caixa'), ('rolo', 'Rolo'),
                    ],
                    default='un', max_length=10,
                )),
                ('justificacao', models.TextField(verbose_name='Justificação')),
                ('observacoes', models.TextField(blank=True)),
                ('estado', models.CharField(
                    choices=[
                        ('pendente', 'Pendente'),
                        ('em_preparacao', 'Em Preparação'),
                        ('entregue', 'Entregue'),
                        ('parcialmente_entregue', 'Parcialmente Entregue'),
                        ('cancelado', 'Cancelado'),
                    ],
                    default='pendente', max_length=25,
                )),
                ('pedido_em', models.DateTimeField(auto_now_add=True)),
                ('processado_em', models.DateTimeField(blank=True, null=True)),
                ('quantidade_entregue', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('material', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pedidos_producao',
                    to='armazem.material',
                )),
                ('ordem', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='pedidos_material',
                    to='producao.ordemproducao',
                )),
                ('pedido_por', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pedidos_material_criados',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('processado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pedidos_material_processados',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Pedido de Material Adicional',
                'verbose_name_plural': 'Pedidos de Material Adicional',
                'ordering': ['-pedido_em'],
            },
        ),
    ]
