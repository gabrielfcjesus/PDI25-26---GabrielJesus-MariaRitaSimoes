from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TarefaMontagem
from apps.producao.models import OrdemProducao, RegistoProducao
from apps.expedicao.models import Expedicao
from apps.core.permissions import departamento_required
from apps.core.models import User


@login_required
@departamento_required(['montagem', 'direcao'])
def menu(request):
    return render(request, 'montagem/menu.html')


@login_required
@departamento_required(['montagem', 'direcao'])
def tarefas_lista(request):
    tarefas = TarefaMontagem.objects.select_related('ordem', 'ordem__cliente', 'responsavel').all()
    return render(request, 'montagem/tarefas/lista.html', {'tarefas': tarefas})


@login_required
@departamento_required(['montagem', 'direcao'])
def criar(request):
    ordens = OrdemProducao.objects.filter(estado='expedicao').select_related('cliente')
    colaboradores_disponiveis = User.objects.filter(ativo=True).select_related('departamento').order_by('first_name', 'last_name')
    if request.method == 'POST':
        ordem_id = request.POST.get('ordem')
        titulo = request.POST.get('titulo')
        if ordem_id and titulo:
            op = get_object_or_404(OrdemProducao, pk=ordem_id, estado='expedicao')
            try:
                hh = int(request.POST.get('tempo_hh') or 0)
                mm = int(request.POST.get('tempo_mm') or 0)
                ss = int(request.POST.get('tempo_ss') or 0)
                tempo = timedelta(hours=hh, minutes=mm, seconds=ss) if (hh or mm or ss) else None
            except (ValueError, TypeError):
                tempo = None
            tarefa = TarefaMontagem.objects.create(
                ordem=op, titulo=titulo,
                descricao=request.POST.get('descricao', ''),
                tempo_previsto=tempo,
                responsavel=request.user,
            )
            colaborador_ids = request.POST.getlist('colaboradores')
            if colaborador_ids:
                tarefa.colaboradores.set(User.objects.filter(pk__in=colaborador_ids))
            op.estado = 'montagem'
            op.save()
            RegistoProducao.objects.create(
                ordem=op,
                utilizador=request.user,
                descricao=f"Tarefa de montagem criada: {titulo}. OP avançou para Montagem.",
            )
            messages.success(request, f'Tarefa criada. OP {op.referencia} avançou para Montagem.')
            return redirect('montagem:tarefas')
    return render(request, 'montagem/tarefas/criar.html', {
        'ordens': ordens,
        'colaboradores_disponiveis': colaboradores_disponiveis,
    })


@login_required
@departamento_required(['montagem', 'direcao'])
def guias_lista(request):
    guias = Expedicao.objects.filter(
        ordem__estado__in=['expedicao', 'montagem']
    ).select_related('ordem', 'ordem__cliente', 'responsavel').order_by('-criado_em')
    return render(request, 'montagem/guias/lista.html', {'guias': guias})


@login_required
@departamento_required(['montagem', 'direcao'])
def guia_detalhe(request, pk):
    guia = get_object_or_404(
        Expedicao.objects.select_related('ordem', 'ordem__cliente', 'responsavel'),
        pk=pk
    )
    return render(request, 'montagem/guias/detalhe.html', {'guia': guia})
