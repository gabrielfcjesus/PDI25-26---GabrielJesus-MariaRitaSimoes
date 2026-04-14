"""
apps/rh/views.py
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trabalhador
from apps.core.models import Departamento
from apps.core.permissions import departamento_required


@login_required
@departamento_required(['rh', 'direcao'])
def trabalhadores_lista(request):
    ordenar = request.GET.get('ordenar', 'nome')
    direcao = request.GET.get('dir', 'asc')

    campos = {
        'nome': 'nome',
        'departamento': 'departamento__nome',
        'cargo': 'cargo__nome',
        'estado': 'estado',
    }
    campo = campos.get(ordenar, 'nome')
    if direcao == 'desc':
        campo = f'-{campo}'

    qs = Trabalhador.objects.select_related('departamento', 'cargo')

    q = request.GET.get('q', '').strip()
    dep_id = request.GET.get('departamento', '')

    if q:
        qs = qs.filter(nome__icontains=q)
    if dep_id:
        qs = qs.filter(departamento_id=dep_id)

    trabalhadores = qs.order_by(campo)
    return render(request, 'rh/trabalhadores/lista.html', {
        'trabalhadores': trabalhadores,
        'titulo': 'Recursos Humanos',
        'ordenar': request.GET.get('ordenar', 'nome'),
        'dir': direcao,
        'colunas': [('nome', 'Nome'), ('departamento', 'Departamento'), ('cargo', 'Cargo')],
        'departamentos': Departamento.objects.order_by('nome'),
        'q': q,
        'dep_id': dep_id,
    })


@login_required
@departamento_required(['rh', 'direcao'])
def trabalhador_detalhe(request, pk):
    t = get_object_or_404(Trabalhador, pk=pk)
    return render(request, 'rh/trabalhadores/detalhe.html', {'trabalhador': t})
