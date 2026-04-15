from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import OrdemProducao, PedidoMaterialAdicional, PedidoAssistencia, RegistoProducao
from modulos.armazem.models import Material, MovimentoStock
from modulos.core.permissions import departamento_required


@login_required
@departamento_required(['producao', 'direcao'])
def menu(request):
    return render(request, 'producao/menu.html', {'titulo': 'Produção'})


@login_required
@departamento_required(['producao', 'direcao'])
def ordens_lista(request):
    ordens = OrdemProducao.objects.select_related('cliente', 'responsavel').all()
    return render(request, 'producao/ordens/lista.html', {'ordens': ordens})


@login_required
@departamento_required(['producao', 'armazem', 'direcao'])
def op_detalhe(request, pk):
    """Detalhe completo de uma OP: info, materiais planeados, pedidos adicionais e histórico."""
    op = get_object_or_404(
        OrdemProducao.objects.select_related('cliente', 'responsavel', 'criado_por'),
        pk=pk
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'iniciar' and op.estado == 'planeamento':
            op.estado = 'em_producao'
            if not op.data_real_inicio:
                op.data_real_inicio = timezone.now()
            op.save()
            RegistoProducao.objects.create(ordem=op, utilizador=request.user, descricao='Produção iniciada.')
            messages.success(request, 'Produção iniciada.')
        elif action == 'pausar' and op.estado == 'em_producao':
            op.estado = 'pausada'
            op.save()
            RegistoProducao.objects.create(ordem=op, utilizador=request.user, descricao='Produção pausada.')
            messages.info(request, 'Produção pausada.')
        elif action == 'retomar' and op.estado == 'pausada':
            op.estado = 'em_producao'
            op.save()
            RegistoProducao.objects.create(ordem=op, utilizador=request.user, descricao='Produção retomada.')
            messages.success(request, 'Produção retomada.')
        elif action == 'terminar' and op.estado in ('em_producao', 'pausada'):
            op.estado = 'qualidade'
            if not op.data_real_fim:
                op.data_real_fim = timezone.now()
            op.save()
            RegistoProducao.objects.create(ordem=op, utilizador=request.user, descricao='Produção terminada — enviada para Qualidade.')
            messages.success(request, f'OP {op.referencia} terminada — disponível em Qualidade.')
        return redirect('producao:op-detalhe', pk=pk)

    itens = op.itens.select_related('material').all()
    pedidos = op.pedidos_material.select_related(
        'material', 'pedido_por', 'processado_por'
    ).all()
    registos = op.registos.select_related('utilizador').all()
    return render(request, 'producao/ordens/detalhe.html', {
        'op': op,
        'itens': itens,
        'pedidos': pedidos,
        'registos': registos,
    })


@login_required
@departamento_required(['producao', 'direcao'])
def pedido_material_criar(request, pk):
    """Registo de pedido de material adicional para uma OP."""
    op = get_object_or_404(OrdemProducao, pk=pk)
    materiais = Material.objects.filter(ativo=True).order_by('nome')

    if request.method == 'POST':
        descricao = request.POST.get('descricao_material', '').strip()
        quantidade_str = request.POST.get('quantidade', '').strip()
        justificacao = request.POST.get('justificacao', '').strip()

        if not (descricao and quantidade_str and justificacao):
            messages.error(request, 'Referência do material, quantidade e justificação são obrigatórios.')
        else:
            material_id = request.POST.get('material') or None
            PedidoMaterialAdicional.objects.create(
                ordem=op,
                material_id=material_id,
                descricao_material=descricao,
                quantidade=quantidade_str,
                unidade=request.POST.get('unidade', 'un'),
                justificacao=justificacao,
                observacoes=request.POST.get('observacoes', ''),
                pedido_por=request.user,
            )
            messages.success(request, 'Pedido de material adicional registado.')
            return redirect('producao:op-detalhe', pk=op.pk)

    return render(request, 'producao/ordens/pedido_material.html', {
        'op': op,
        'materiais': materiais,
        'unidade_choices': PedidoMaterialAdicional.UNIDADE_CHOICES,
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def pedido_material_processar(request, pk):
    """Processamento de um pedido de material: regista entrega e gera saída de stock."""
    pedido = get_object_or_404(
        PedidoMaterialAdicional.objects.select_related('ordem', 'material'),
        pk=pk
    )

    if request.method != 'POST':
        return redirect('producao:op-detalhe', pk=pedido.ordem.pk)

    novo_estado = request.POST.get('estado', 'entregue')
    qtd_entregue_str = request.POST.get('quantidade_entregue', '').strip()

    if not qtd_entregue_str:
        messages.error(request, 'Indique a quantidade entregue.')
        return redirect('producao:op-detalhe', pk=pedido.ordem.pk)

    qtd_entregue = float(qtd_entregue_str)
    pedido.estado = novo_estado
    pedido.quantidade_entregue = qtd_entregue
    pedido.processado_por = request.user
    pedido.processado_em = timezone.now()
    pedido.save()

    # Gerar saída de stock se o material estiver associado ao catálogo
    if pedido.material and novo_estado in ('entregue', 'parcialmente_entregue'):
        material = pedido.material
        from decimal import Decimal
        qtd = Decimal(str(qtd_entregue))

        if material.stock_atual >= qtd:
            anterior = material.stock_atual
            material.stock_atual -= qtd
            material.save()
            MovimentoStock.objects.create(
                material=material,
                tipo='saida',
                quantidade=qtd,
                quantidade_anterior=anterior,
                quantidade_posterior=material.stock_atual,
                motivo=f'Material adicional OP {pedido.ordem.referencia}: {pedido.justificacao[:100]}',
                referencia_doc=pedido.ordem.referencia,
                utilizador=request.user,
            )
            messages.success(
                request,
                f'Entrega registada. Saída de stock: {qtd} {pedido.unidade} de "{material.nome}".'
            )
        else:
            messages.warning(
                request,
                f'Stock insuficiente para "{material.nome}" (stock actual: {material.stock_atual}). '
                f'Pedido atualizado mas saída de stock não foi registada.'
            )
    else:
        messages.success(request, 'Pedido atualizado com sucesso.')

    return redirect('producao:op-detalhe', pk=pedido.ordem.pk)


@login_required
@departamento_required(['producao', 'direcao'])
def atualizar_estado(request):
    """Listagem de OPs para atualizar estado."""
    ESTADOS_PRODUCAO = [
        ('planeamento', 'Pendente'),
        ('em_producao', 'Em Produção'),
        ('qualidade', 'Finalizada'),
    ]
    ordens = OrdemProducao.objects.select_related('cliente', 'responsavel').filter(
        estado__in=['planeamento', 'em_producao']
    )
    if request.method == 'POST':
        op_pk = request.POST.get('op')
        novo_estado = request.POST.get('estado')
        op = get_object_or_404(OrdemProducao, pk=op_pk)
        if novo_estado in dict(ESTADOS_PRODUCAO):
            op.estado = novo_estado
            if novo_estado == 'em_producao' and not op.data_real_inicio:
                op.data_real_inicio = timezone.now()
            if novo_estado == 'qualidade' and not op.data_real_fim:
                op.data_real_fim = timezone.now()
            op.save()
            label = dict(ESTADOS_PRODUCAO)[novo_estado]
            RegistoProducao.objects.create(
                ordem=op,
                utilizador=request.user,
                descricao=f'Estado alterado para: {label}',
            )
            messages.success(request, f'OP {op.referencia} marcada como "{label}".')
            return redirect('producao:atualizar-estado')
        messages.error(request, 'Estado inválido.')
    return render(request, 'producao/atualizar_estado.html', {
        'ordens': ordens,
        'estado_choices': ESTADOS_PRODUCAO,
    })


@login_required
@departamento_required(['producao', 'direcao'])
def pedir_assistencia(request):
    """Formulário para criar pedido de assistência."""
    ordens = OrdemProducao.objects.select_related('cliente').exclude(
        estado__in=['concluida', 'cancelada']
    ).order_by('-criado_em')

    if request.method == 'POST':
        op_pk = request.POST.get('op')
        descricao = request.POST.get('descricao', '').strip()
        urgencia = request.POST.get('urgencia', 'normal')

        if not op_pk or not descricao:
            messages.error(request, 'Selecione uma OP e descreva o problema.')
        else:
            op = get_object_or_404(OrdemProducao, pk=op_pk)
            PedidoAssistencia.objects.create(
                ordem=op,
                descricao=descricao,
                urgencia=urgencia,
                criado_por=request.user,
            )
            messages.success(request, f'Pedido de assistência enviado para a OP {op.referencia}.')
            return redirect('producao:menu')

    return render(request, 'producao/pedir_assistencia.html', {
        'ordens': ordens,
        'urgencia_choices': PedidoAssistencia.URGENCIA_CHOICES,
    })


@login_required
@departamento_required(['planeamento', 'direcao'])
def assistencias_lista(request):
    """Lista de pedidos de assistência."""
    pedidos = PedidoAssistencia.objects.select_related(
        'ordem', 'ordem__cliente', 'criado_por', 'respondido_por'
    ).all()
    return render(request, 'producao/assistencias/lista.html', {'pedidos': pedidos})


@login_required
@departamento_required(['planeamento', 'direcao'])
def assistencia_responder(request, pk):
    """Responder / atualizar um pedido de assistência."""
    pedido = get_object_or_404(
        PedidoAssistencia.objects.select_related('ordem', 'criado_por'),
        pk=pk
    )

    if request.method == 'POST':
        resposta = request.POST.get('resposta', '').strip()
        novo_estado = request.POST.get('estado', 'em_analise')
        if not resposta:
            messages.error(request, 'A resposta não pode estar vazia.')
        else:
            pedido.resposta = resposta
            pedido.estado = novo_estado
            pedido.respondido_por = request.user
            pedido.respondido_em = timezone.now()
            pedido.save()
            messages.success(request, 'Resposta registada com sucesso.')
            return redirect('producao:assistencias')

    return render(request, 'producao/assistencias/responder.html', {'pedido': pedido})
