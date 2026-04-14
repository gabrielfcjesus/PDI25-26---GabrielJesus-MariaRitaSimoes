"""apps/armazem/views.py"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Material, MovimentoStock, Categoria, PedidoCompra, ItemPedidoCompra
from apps.core.permissions import departamento_required
from django import forms


class MovimentoForm(forms.Form):
    TIPO_CHOICES = [('entrada', 'Entrada'), ('saida', 'Saída'), ('ajuste', 'Ajuste')]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    quantidade = forms.DecimalField(min_value=0.01, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    motivo = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


@login_required
@departamento_required(['armazem', 'direcao'])
def materiais_lista(request):
    materiais = Material.objects.select_related('categoria').filter(ativo=True)
    categorias = Categoria.objects.all().order_by('nome')

    q = request.GET.get('q', '').strip()
    cat = request.GET.get('categoria', '').strip()

    if q:
        materiais = materiais.filter(nome__icontains=q) | materiais.filter(referencia__icontains=q)
    if cat:
        materiais = materiais.filter(categoria_id=cat)

    return render(request, 'armazem/materiais/lista.html', {
        'materiais': materiais,
        'categorias': categorias,
        'q': q,
        'categoria_sel': cat,
        'titulo': 'Armazem',
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def material_detalhe(request, pk):
    material = get_object_or_404(Material, pk=pk)
    movimentos = material.movimentos.all()[:20]
    form = MovimentoForm()

    if request.method == 'POST':
        form = MovimentoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            qtd = form.cleaned_data['quantidade']
            anterior = material.stock_atual

            if tipo == 'entrada':
                material.stock_atual += qtd
            elif tipo == 'saida':
                if qtd > material.stock_atual:
                    messages.error(request, 'Stock insuficiente.')
                    return redirect('armazem:material-detalhe', pk=pk)
                material.stock_atual -= qtd
            else:  # ajuste
                material.stock_atual = qtd

            material.save()
            MovimentoStock.objects.create(
                material=material, tipo=tipo,
                quantidade=qtd, quantidade_anterior=anterior,
                quantidade_posterior=material.stock_atual,
                motivo=form.cleaned_data['motivo'],
                utilizador=request.user
            )
            messages.success(request, 'Movimento registado.')
            return redirect('armazem:material-detalhe', pk=pk)

    return render(request, 'armazem/materiais/detalhe.html', {
        'material': material, 'movimentos': movimentos, 'form': form
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def material_criar(request):
    categorias = Categoria.objects.all().order_by('nome')
    unidades = Material.UNIDADE_CHOICES

    if request.method == 'POST':
        referencia = request.POST.get('referencia', '').strip()
        nome = request.POST.get('nome', '').strip()
        categoria_id = request.POST.get('categoria', '').strip() or None
        descricao = request.POST.get('descricao', '').strip()
        unidade = request.POST.get('unidade', 'un')
        stock_atual = request.POST.get('stock_atual', '0').strip() or '0'
        stock_minimo = request.POST.get('stock_minimo', '0').strip() or '0'
        localizacao = request.POST.get('localizacao', '').strip()

        if not referencia or not nome:
            messages.error(request, 'Referência e Nome são obrigatórios.')
        elif Material.objects.filter(referencia=referencia).exists():
            messages.error(request, f'Já existe um material com a referência "{referencia}".')
        else:
            categoria = Categoria.objects.get(pk=categoria_id) if categoria_id else None
            Material.objects.create(
                referencia=referencia,
                nome=nome,
                categoria=categoria,
                descricao=descricao,
                unidade=unidade,
                stock_atual=stock_atual,
                stock_minimo=stock_minimo,
                localizacao=localizacao,
            )
            messages.success(request, f'Material "{nome}" criado com sucesso.')
            return redirect('armazem:materiais')

    return render(request, 'armazem/materiais/criar.html', {
        'categorias': categorias,
        'unidades': unidades,
    })


@login_required
def materiais_pesquisar(request):
    """Endpoint JSON para pesquisa de materiais (usado no picker da criação de OP)."""
    from django.http import JsonResponse
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('categoria', '').strip()

    qs = Material.objects.filter(ativo=True).select_related('categoria')
    if q:
        qs = qs.filter(nome__icontains=q) | qs.filter(referencia__icontains=q)
    if cat:
        qs = qs.filter(categoria_id=cat)

    resultados = [
        {
            'id': m.pk,
            'referencia': m.referencia,
            'nome': m.nome,
            'unidade': m.get_unidade_display(),
            'stock': str(m.stock_atual),
            'categoria': m.categoria.nome if m.categoria else '',
        }
        for m in qs.order_by('nome')[:30]
    ]
    return JsonResponse({'resultados': resultados})


@login_required
@departamento_required(['armazem', 'direcao'])
def armazem_menu(request):
    from django.shortcuts import render
    return render(request, 'armazem/menu.html')


# ─── Ordens de Compra ───────────────────────────────────────────────────────

@login_required
@departamento_required(['armazem', 'direcao'])
def pedidos_lista(request):
    pedidos = PedidoCompra.objects.prefetch_related('itens').all()
    estado_sel = request.GET.get('estado', '').strip()
    if estado_sel:
        pedidos = pedidos.filter(estado=estado_sel)
    return render(request, 'armazem/pedidos/lista.html', {
        'pedidos': pedidos,
        'estados': PedidoCompra.ESTADO_CHOICES,
        'estado_sel': estado_sel,
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def pedido_criar(request):
    if request.method == 'POST':
        fornecedor = request.POST.get('fornecedor', '').strip()
        data_entrega = request.POST.get('data_entrega_prevista', '').strip() or None
        observacoes = request.POST.get('observacoes', '').strip()
        material_ids = request.POST.getlist('material_id')
        quantidades = request.POST.getlist('quantidade')

        if not fornecedor:
            messages.error(request, 'O fornecedor é obrigatório.')
            return redirect('armazem:pedido-criar')

        # Filtrar linhas válidas
        itens_validos = [
            (mid, qtd)
            for mid, qtd in zip(material_ids, quantidades)
            if mid and qtd
        ]
        if not itens_validos:
            messages.error(request, 'Adicione pelo menos um material.')
            return redirect('armazem:pedido-criar')

        pedido = PedidoCompra.objects.create(
            fornecedor=fornecedor,
            data_entrega_prevista=data_entrega if data_entrega else None,
            observacoes=observacoes,
            criado_por=request.user,
        )
        for mid, qtd in itens_validos:
            try:
                material = Material.objects.get(pk=mid)
                ItemPedidoCompra.objects.create(
                    pedido=pedido,
                    material=material,
                    quantidade=qtd,
                )
            except (Material.DoesNotExist, Exception):
                pass

        messages.success(request, f'Ordem de compra {pedido.referencia} criada.')
        return redirect('armazem:pedido-detalhe', pk=pedido.pk)

    return render(request, 'armazem/pedidos/criar.html', {
        'categorias': Categoria.objects.all().order_by('nome'),
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def pedido_detalhe(request, pk):
    pedido = get_object_or_404(PedidoCompra, pk=pk)
    itens = pedido.itens.select_related('material').all()
    return render(request, 'armazem/pedidos/detalhe.html', {
        'pedido': pedido,
        'itens': itens,
    })


@login_required
@departamento_required(['armazem', 'direcao'])
def pedido_acao(request, pk):
    if request.method != 'POST':
        return redirect('armazem:pedido-detalhe', pk=pk)

    pedido = get_object_or_404(PedidoCompra, pk=pk)
    action = request.POST.get('action')

    transicoes = {
        'aprovar': ('pendente', 'aprovado'),
        'enviar': ('aprovado', 'enviado'),
        'cancelar': (None, 'cancelado'),  # None = qualquer estado
    }

    if action in transicoes:
        estado_req, estado_novo = transicoes[action]
        if estado_req is None or pedido.estado == estado_req:
            pedido.estado = estado_novo
            pedido.save()
            messages.success(request, f'Estado atualizado para: {pedido.get_estado_display()}')
        else:
            messages.error(request, 'Transição de estado inválida.')

    elif action == 'receber':
        from django.utils import timezone
        itens = pedido.itens.select_related('material').all()
        algum_recebido = False

        for item in itens:
            qty_str = request.POST.get(f'qty_{item.pk}', '').strip()
            if not qty_str:
                continue
            try:
                qty = float(qty_str)
            except ValueError:
                continue
            if qty <= 0:
                continue

            por_receber = float(item.por_receber)
            qty_real = min(qty, por_receber)
            if qty_real <= 0:
                continue

            anterior = item.material.stock_atual
            item.material.stock_atual += qty_real
            item.material.save()
            item.qty_recebida += qty_real
            item.save()

            MovimentoStock.objects.create(
                material=item.material,
                tipo='entrada',
                quantidade=qty_real,
                quantidade_anterior=anterior,
                quantidade_posterior=item.material.stock_atual,
                motivo=f'Receção OC {pedido.referencia}',
                referencia_doc=pedido.referencia,
                utilizador=request.user,
            )
            algum_recebido = True

        if algum_recebido:
            # Reavalia estado
            itens_refresh = pedido.itens.all()
            todos_recebidos = all(i.qty_recebida >= i.quantidade for i in itens_refresh)
            if todos_recebidos:
                pedido.estado = 'recebido'
                pedido.data_entrega_real = timezone.now().date()
            else:
                pedido.estado = 'parcialmente_recebido'
            pedido.save()
            messages.success(request, 'Receção registada e stock atualizado.')
        else:
            messages.warning(request, 'Nenhuma quantidade foi introduzida.')

    return redirect('armazem:pedido-detalhe', pk=pk)
