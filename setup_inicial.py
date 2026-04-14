"""
Script para popular dados iniciais (departamentos, cargos e superuser)
Executar com: python manage.py shell < setup_inicial.py
Ou: python manage.py runscript setup_inicial  (com django-extensions)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import Departamento, Cargo, User

# ─── Departamentos ───────────────────────────────────────────────
departamentos_data = [
    ('direcao',    'Direção / Administração'),
    ('rh',         'Recursos Humanos'),
    ('armazem',    'Armazém'),
    ('planeamento','Planeamento'),
    ('producao',   'Produção'),
    ('qualidade',  'Controlo de Qualidade'),
    ('expedicao',  'Expedição'),
    ('montagem',   'Montagem'),
]

print("A criar departamentos...")
departamentos = {}
for codigo, nome in departamentos_data:
    dep, created = Departamento.objects.get_or_create(codigo=codigo, defaults={'nome': nome})
    departamentos[codigo] = dep
    print(f"  {'✔ Criado' if created else '  Existe'}: {nome}")

# ─── Cargos base ────────────────────────────────────────────────
cargos_data = [
    ('direcao',    'Diretor Geral'),
    ('direcao',    'Administrador'),
    ('rh',         'Técnico de RH'),
    ('rh',         'Responsável de RH'),
    ('armazem',    'Operador de Armazém'),
    ('armazem',    'Responsável de Armazém'),
    ('planeamento','Técnico de Planeamento'),
    ('planeamento','Responsável de Planeamento'),
    ('producao',   'Operador de Produção'),
    ('producao',   'Chefe de Produção'),
    ('qualidade',  'Técnico de Qualidade'),
    ('qualidade',  'Responsável de Qualidade'),
    ('expedicao',  'Operador de Expedição'),
    ('expedicao',  'Responsável de Expedição'),
    ('montagem',   'Técnico de Montagem'),
    ('montagem',   'Chefe de Montagem'),
]

print("\nA criar cargos...")
for dep_codigo, nome_cargo in cargos_data:
    cargo, created = Cargo.objects.get_or_create(
        nome=nome_cargo,
        departamento=departamentos[dep_codigo]
    )
    print(f"  {'✔ Criado' if created else '  Existe'}: {nome_cargo}")

# ─── Superuser (Admin) ──────────────────────────────────────────
print("\nA criar superuser 'admin'...")
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        password='admin123',
        first_name='Administrador',
        last_name='PrimeTool',
        email='admin@primetool.pt',
        departamento=departamentos['direcao'],
    )
    print("  ✔ Superuser criado: admin / admin123")
else:
    print("  Superuser já existe.")

print("\n✅ Setup inicial concluído!")
print("   Login: http://localhost:8000/login/")
print("   Admin: http://localhost:8000/admin/")
