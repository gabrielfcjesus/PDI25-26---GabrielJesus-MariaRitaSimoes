from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expedicao', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Veiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=20, unique=True)),
                ('descricao', models.CharField(max_length=100)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Veículo',
                'verbose_name_plural': 'Veículos',
                'ordering': ['matricula'],
            },
        ),
    ]
