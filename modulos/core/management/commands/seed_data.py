"""
Management command para popular dados de teste.
Uso: python manage.py seed_data
     python manage.py seed_data --reset
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Popula a base de dados com dados de teste (utilizadores, materiais, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Apaga dados existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset_data()

        with transaction.atomic():
            departamentos = self._criar_departamentos()
            self._criar_utilizadores(departamentos)
            self._criar_materiais()
            self._criar_clientes()

        self.stdout.write(self.style.SUCCESS('\nSeed data concluido com sucesso!'))

    # ─── Reset ────────────────────────────────────────────────────────────────

    def _reset_data(self):
        from modulos.core.models import User
        from modulos.armazem.models import Material, Categoria, MovimentoStock

        self.stdout.write('A limpar dados existentes...')
        MovimentoStock.objects.all().delete()
        Material.objects.all().delete()
        Categoria.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('  Dados de teste removidos.'))

    # ─── Departamentos ────────────────────────────────────────────────────────

    def _criar_departamentos(self):
        from modulos.core.models import Departamento, Cargo

        self.stdout.write('A verificar departamentos e cargos...')

        departamentos_data = [
            ('direcao',     'Direção / Administração'),
            ('rh',          'Recursos Humanos'),
            ('armazem',     'Armazém'),
            ('planeamento', 'Planeamento'),
            ('producao',    'Produção'),
            ('qualidade',   'Controlo de Qualidade'),
            ('expedicao',   'Expedição'),
            ('montagem',    'Montagem'),
        ]

        cargos_data = [
            ('direcao',     'Diretor Geral'),
            ('direcao',     'Administrador'),
            ('rh',          'Técnico de RH'),
            ('rh',          'Responsável de RH'),
            ('armazem',     'Operador de Armazém'),
            ('armazem',     'Responsável de Armazém'),
            ('planeamento', 'Técnico de Planeamento'),
            ('planeamento', 'Responsável de Planeamento'),
            ('producao',    'Operador de Produção'),
            ('producao',    'Chefe de Produção'),
            ('qualidade',   'Técnico de Qualidade'),
            ('qualidade',   'Responsável de Qualidade'),
            ('expedicao',   'Operador de Expedição'),
            ('expedicao',   'Responsável de Expedição'),
            ('montagem',    'Técnico de Montagem'),
            ('montagem',    'Chefe de Montagem'),
        ]

        departamentos = {}
        for codigo, nome in departamentos_data:
            dep, _ = Departamento.objects.get_or_create(codigo=codigo, defaults={'nome': nome})
            departamentos[codigo] = dep

        for dep_codigo, nome_cargo in cargos_data:
            Cargo.objects.get_or_create(
                nome=nome_cargo,
                departamento=departamentos[dep_codigo]
            )

        self.stdout.write(self.style.SUCCESS('  OK'))
        return departamentos

    # ─── Utilizadores ─────────────────────────────────────────────────────────

    def _criar_utilizadores(self, departamentos):
        from modulos.core.models import User, Cargo

        self.stdout.write('\nA criar utilizadores...')

        utilizadores = [
            {
                'username': 'admin',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': 'PrimeTool',
                'email': 'admin@primetool.pt',
                'departamento': 'direcao',
                'cargo': 'Diretor Geral',
                'is_superuser': True,
                'is_staff': True,
            },
        ]

        for dados in utilizadores:
            dep_codigo = dados.pop('departamento')
            cargo_nome = dados.pop('cargo')
            password = dados.pop('password')
            is_superuser = dados.pop('is_superuser', False)
            is_staff = dados.pop('is_staff', False)

            dep = departamentos.get(dep_codigo)
            cargo = Cargo.objects.filter(nome=cargo_nome, departamento=dep).first()

            if User.objects.filter(username=dados['username']).exists():
                self.stdout.write(f"  Existe: {dados['username']}")
                continue

            if is_superuser:
                user = User.objects.create_superuser(
                    departamento=dep,
                    cargo=cargo,
                    **dados
                )
                user.set_password(password)
                user.save()
            else:
                user = User.objects.create_user(
                    password=password,
                    departamento=dep,
                    cargo=cargo,
                    **dados
                )

            self.stdout.write(self.style.SUCCESS(
                f'  Criado: {user.get_full_name()} ({dep_codigo}) — {user.username} / {password}'
            ))

    # ─── Clientes ─────────────────────────────────────────────────────────────

    def _criar_clientes(self):
        from modulos.planeamento.models import Cliente

        self.stdout.write('\nA criar clientes...')

        clientes_data = [
            ('Metalofab, Lda',          '501234567', 'geral@metalofab.pt',        '253 100 200', 'Rua da Industria, 12, Braga'),
            ('Construções Soares & Filhos', '502345678', 'geral@soaresfilhos.pt', '222 300 400', 'Av. Central, 45, Coimbra'),
            ('EDP Distribuição',         '503456789', 'contratos@edp.pt',          '210 500 600', 'Praça Marquês de Pombal, 1, Lisboa'),
            ('Grupo Mota-Engil',         '504567890', 'obras@mota-engil.pt',       '229 700 800', 'Rua do General Norton de Matos, Porto'),
            ('Ascendi Operações, SA',    '505678901', 'manutencao@ascendi.pt',     '239 900 100', 'Zona Industrial de Aveiro'),
            ('Infraestruturas de Portugal', '506789012', 'obras@infraestruturaspt.pt', '213 100 200', 'Praça da Figueira, Lisboa'),
            ('Câmara Municipal de Guimarães', '507890123', 'obras@cm-guimaraes.pt', '253 400 500', 'Praça Municipal, Guimarães'),
            ('Lucios Construção, SA',    '508901234', 'geral@lucios.pt',            '265 600 700', 'Estrada Nacional 10, Setúbal'),
        ]

        criados = 0
        for nome, nif, email, telefone, morada in clientes_data:
            _, created = Cliente.objects.get_or_create(
                nif=nif,
                defaults={'nome': nome, 'email': email, 'telefone': telefone, 'morada': morada}
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(f'  {criados} clientes criados.'))

    # ─── Materiais ────────────────────────────────────────────────────────────

    def _criar_materiais(self):
        from modulos.armazem.models import Categoria, Material

        self.stdout.write('\nA criar categorias e materiais...')

        categorias_data = [
            'Chapas',
            'Perfis',
            'Tubos',
            'Parafusos e Fixadores',
            'Consumíveis de Soldadura',
            'Ferramentas',
            'EPI',
            'Tintas e Tratamentos',
        ]

        categorias = {}
        for nome in categorias_data:
            cat, _ = Categoria.objects.get_or_create(nome=nome)
            categorias[nome] = cat

        materiais_data = [
            # Chapas
            ('ACO-001', 'Chapa de Aço 3mm (1250x2500)',    'Chapas',                  'un',   45,  10, 'A1-P2'),
            ('ACO-002', 'Chapa de Aço 2mm (1250x2500)',    'Chapas',                  'un',    8,  10, 'A1-P3'),
            ('ACO-003', 'Chapa de Aço 5mm (1250x2500)',    'Chapas',                  'un',   20,   8, 'A1-P4'),
            ('ACO-004', 'Chapa Galvanizada 1.5mm (1000x2000)', 'Chapas',              'un',   15,   5, 'A1-P5'),
            ('INX-001', 'Chapa Inox 304 2mm (1000x2000)',  'Chapas',                  'un',    6,   4, 'A2-P1'),

            # Perfis
            ('PER-001', 'Perfil IPE 200 (6ml)',            'Perfis',                  'un',   32,   5, 'B2-P1'),
            ('PER-002', 'Perfil Tubular 40x40x3 (6ml)',    'Perfis',                  'un',    0,   8, 'B2-P2'),
            ('PER-003', 'Perfil UPN 120 (6ml)',            'Perfis',                  'un',   18,   5, 'B2-P3'),
            ('PER-004', 'Cantoneira 50x50x5 (6ml)',        'Perfis',                  'un',   24,   6, 'B2-P4'),
            ('PER-005', 'Perfil HEA 160 (6ml)',            'Perfis',                  'un',   10,   4, 'B2-P5'),

            # Tubos
            ('TUB-001', 'Tubo Redondo 60.3x3 (6ml)',      'Tubos',                   'un',   14,   5, 'B3-P1'),
            ('TUB-002', 'Tubo Quadrado 50x50x2 (6ml)',    'Tubos',                   'un',    3,   6, 'B3-P2'),
            ('TUB-003', 'Tubo Rectangular 80x40x3 (6ml)', 'Tubos',                   'un',   22,   5, 'B3-P3'),

            # Parafusos e Fixadores
            ('FIX-001', 'Parafuso M12x40 8.8 (caixa 50)', 'Parafusos e Fixadores',   'caixa', 12,  5, 'C1-P1'),
            ('FIX-002', 'Parafuso M16x60 8.8 (caixa 25)', 'Parafusos e Fixadores',   'caixa',  4,  5, 'C1-P2'),
            ('FIX-003', 'Porca M12 (caixa 100)',           'Parafusos e Fixadores',   'caixa', 20,  8, 'C1-P3'),
            ('FIX-004', 'Anilha M12 (caixa 200)',          'Parafusos e Fixadores',   'caixa', 15,  8, 'C1-P4'),
            ('FIX-005', 'Rebite Pop 4.8x12 (caixa 500)',   'Parafusos e Fixadores',   'caixa',  2, 10, 'C1-P5'),

            # Consumíveis de Soldadura
            ('SOL-001', 'Fio de Soldadura MIG ER70S-6 0.8mm (15kg)', 'Consumíveis de Soldadura', 'un', 8, 3, 'D1-P1'),
            ('SOL-002', 'Eléctrodo E6013 3.2mm (5kg)',    'Consumíveis de Soldadura', 'un',    5,   2, 'D1-P2'),
            ('SOL-003', 'Disco de Corte 230x2mm',         'Consumíveis de Soldadura', 'un',   45,  20, 'D1-P3'),
            ('SOL-004', 'Disco de Desbaste 230x6mm',      'Consumíveis de Soldadura', 'un',   30,  15, 'D1-P4'),
            ('SOL-005', 'Gás CO2/Argon MIX (botija 20L)', 'Consumíveis de Soldadura', 'un',    3,   2, 'D1-P5'),

            # Ferramentas
            ('FER-001', 'Rebarbadora Bosch 230mm',        'Ferramentas',              'un',    4,   2, 'E1-P1'),
            ('FER-002', 'Berbequim Makita 18V',           'Ferramentas',              'un',    3,   2, 'E1-P2'),

            # EPI
            ('EPI-001', 'Capacete de Segurança',          'EPI',                      'un',   20,  10, 'F1-P1'),
            ('EPI-002', 'Luvas de Soldador (par)',        'EPI',                      'un',   35,  15, 'F1-P2'),
            ('EPI-003', 'Óculos de Proteção',             'EPI',                      'un',   18,  10, 'F1-P3'),
            ('EPI-004', 'Botas de Segurança S3 (par)',    'EPI',                      'un',    6,   4, 'F1-P4'),

            # Tintas e Tratamentos
            ('TIN-001', 'Primário Anticorrosão Cinza (5L)', 'Tintas e Tratamentos',   'un',    8,   3, 'G1-P1'),
            ('TIN-002', 'Tinta de Acabamento RAL 7035 (5L)', 'Tintas e Tratamentos',  'un',    5,   2, 'G1-P2'),
            ('TIN-003', 'Galvanização a Frio (spray 400ml)', 'Tintas e Tratamentos',  'un',   14,   6, 'G1-P3'),
        ]

        criados = 0
        for ref, nome, cat_nome, unidade, stock, stock_min, localizacao in materiais_data:
            _, created = Material.objects.get_or_create(
                referencia=ref,
                defaults={
                    'nome': nome,
                    'categoria': categorias[cat_nome],
                    'unidade': unidade,
                    'stock_atual': stock,
                    'stock_minimo': stock_min,
                    'localizacao': localizacao,
                }
            )
            if created:
                criados += 1

        self.stdout.write(self.style.SUCCESS(f'  {criados} materiais criados ({len(materiais_data)} total).'))
