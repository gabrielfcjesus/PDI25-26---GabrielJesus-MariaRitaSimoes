from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('montagem', '0002_tarefamontagem_colaboradores'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefamontagem',
            name='tempo_previsto',
            field=models.DurationField(blank=True, null=True, verbose_name='Tempo previsto'),
        ),
    ]
