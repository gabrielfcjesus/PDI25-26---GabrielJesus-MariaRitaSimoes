import random
from django.db import migrations, models


def preencher_codigos_at(apps, schema_editor):
    Expedicao = apps.get_model('expedicao', 'Expedicao')
    usados = set()
    for exp in Expedicao.objects.all():
        codigo = str(random.randint(100000000000, 999999999999))
        while codigo in usados:
            codigo = str(random.randint(100000000000, 999999999999))
        exp.codigo_at = codigo
        exp.save()
        usados.add(codigo)


class Migration(migrations.Migration):

    dependencies = [
        ('expedicao', '0002_veiculo'),
    ]

    operations = [
        migrations.AddField(
            model_name='expedicao',
            name='codigo_at',
            field=models.CharField(blank=True, max_length=12, default=''),
        ),
        migrations.RunPython(preencher_codigos_at, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='expedicao',
            name='codigo_at',
            field=models.CharField(blank=True, max_length=12, unique=True),
        ),
    ]
