from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expedicao, Veiculo
from modulos.producao.models import OrdemProducao, RegistoProducao
from modulos.core.permissions import departamento_required
from modulos.qualidade.models import InspecaoQualidade


@login_required
@departamento_required(['expedicao', 'direcao'])
def menu(request):
    return render(request, 'expedicao/menu.html')


@login_required
@departamento_required(['expedicao', 'direcao'])
def expedicoes_lista(request):
    expedicoes = Expedicao.objects.select_related('ordem', 'ordem__cliente', 'responsavel').all()
    return render(request, 'expedicao/lista.html', {'expedicoes': expedicoes})


@login_required
@departamento_required(['expedicao', 'direcao'])
def criar(request):
    # OPs com verificação final aprovada
    ordens_finais = list(
        OrdemProducao.objects.filter(estado='expedicao').select_related('cliente')
    )
    # OPs com apenas verificação intermédia aprovada (ainda em estado 'qualidade')
    ops_intermedia_ids = InspecaoQualidade.objects.filter(
        tipo='intermedia',
        resultado__in=('aprovado', 'aprovado_condicional'),
        ordem__estado='qualidade',
    ).values_list('ordem_id', flat=True).distinct()
    ordens_intermedia = list(
        OrdemProducao.objects.filter(pk__in=ops_intermedia_ids).select_related('cliente')
    )
    # Marcar as intermédias para o template
    for op in ordens_intermedia:
        op._apenas_intermedia = True

    ordens = ordens_finais + ordens_intermedia
    veiculos = Veiculo.objects.filter(ativo=True)
    if request.method == 'POST':
        ordem_id = request.POST.get('ordem')
        if ordem_id:
            op = get_object_or_404(OrdemProducao, pk=ordem_id, estado__in=['expedicao', 'qualidade'])
            base_ref = f'EXP-{op.referencia}'
            count = Expedicao.objects.filter(referencia__startswith=base_ref).count()
            ref = base_ref if count == 0 else f'{base_ref}-{count + 1}'
            veiculo_id = request.POST.get('veiculo') or None
            veiculo_label = ''
            if veiculo_id:
                v = Veiculo.objects.filter(pk=veiculo_id).first()
                if v:
                    veiculo_label = str(v)
            from .models import gerar_codigo_at
            exp = Expedicao.objects.create(
                referencia=ref,
                codigo_at=gerar_codigo_at(),
                ordem=op,
                transportadora=veiculo_label,
                data_prevista_envio=request.POST.get('data_prevista_envio') or None,
                morada_entrega=request.POST.get('morada_entrega', ''),
                observacoes=request.POST.get('observacoes', ''),
                responsavel=request.user,
            )
            op.estado = 'expedicao'
            op.save()
            RegistoProducao.objects.create(
                ordem=op,
                utilizador=request.user,
                descricao=f"Guia de transporte criada (Ref: {exp.referencia}). OP avançou para Expedição.",
            )
            messages.success(request, f'Expedição {ref} criada. OP avançou para Expedição.')
            return redirect('expedicao:detalhe', pk=exp.pk)

    return render(request, 'expedicao/criar.html', {
        'ordens': ordens,
        'ordens_intermedia_ids': [op.pk for op in ordens_intermedia],
        'veiculos': veiculos,
    })


@login_required
@departamento_required(['expedicao', 'direcao'])
def detalhe(request, pk):
    exp = get_object_or_404(Expedicao, pk=pk)
    return render(request, 'expedicao/detalhe.html', {'exp': exp})
