from django.core.management.base import BaseCommand
from apps.expedicao.models import Veiculo


class Command(BaseCommand):
    help = 'Cria veículos de expedição de exemplo'

    def handle(self, *args, **options):
        veiculos = [
            ('00-AA-00', 'Mercedes Sprinter — Furgão Grande'),
            ('00-BB-00', 'Volkswagen Crafter — Furgão Médio'),
            ('00-CC-00', 'Ford Transit — Furgão Pequeno'),
            ('00-DD-00', 'Iveco Daily — Caixa Aberta'),
            ('00-EE-00', 'Renault Master — Caixa Fechada'),
        ]
        criados = 0
        for matricula, descricao in veiculos:
            _, created = Veiculo.objects.get_or_create(
                matricula=matricula,
                defaults={'descricao': descricao}
            )
            if created:
                criados += 1
                self.stdout.write(f'  Veiculo criado: {matricula} — {descricao}')

        self.stdout.write(self.style.SUCCESS(f'\n{criados} veiculos criados.'))
