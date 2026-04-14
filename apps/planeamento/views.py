import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from .models import Cliente
from apps.producao.models import OrdemProducao, ItemProducao
from apps.armazem.models import Categoria, Material
from apps.core.permissions import departamento_required


def _gerar_referencia():
    """Gera a proxima referencia no formato YYYY-XXXX."""
    ano = timezone.now().year
    prefix = f"{ano}-"
    ultima = (
        OrdemProducao.objects
        .filter(referencia__startswith=prefix)
        .order_by('-referencia')
        .values_list('referencia', flat=True)
        .first()
    )
    if ultima:
        try:
            num = int(ultima.split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return f"{ano}-{num:04d}"


@login_required
@departamento_required(['planeamento', 'direcao'])
def ops_lista(request):
    ordens = OrdemProducao.objects.select_related('cliente', 'responsavel').all()
    return render(request, 'planeamento/ops/lista.html', {'ordens': ordens})


@login_required
@departamento_required(['planeamento', 'direcao'])
def op_detalhe(request, pk):
    ordem = get_object_or_404(OrdemProducao.objects.select_related('cliente'), pk=pk)
    return render(request, 'planeamento/ops/detalhe.html', {'ordem': ordem})


@login_required
@departamento_required(['planeamento', 'direcao'])
def op_criar(request):
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    proxima_ref = _gerar_referencia()

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cliente_id = request.POST.get('cliente', '').strip()
        data_entrega = request.POST.get('data_entrega_prevista') or None
        data_planeamento_raw = request.POST.get('data_planeamento', '').strip()

        if not nome or not cliente_id:
            messages.error(request, 'Nome da OP e cliente sao obrigatorios.')
        else:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            data_plan = None
            if data_planeamento_raw:
                data_plan = parse_datetime(data_planeamento_raw)
                if data_plan and timezone.is_naive(data_plan):
                    data_plan = timezone.make_aware(data_plan)
            if not data_plan:
                data_plan = timezone.now()
            referencia = _gerar_referencia()
            op = OrdemProducao.objects.create(
                referencia=referencia,
                nome=nome,
                cliente_id=cliente_id,
                data_entrega_prevista=data_entrega,
                prioridade=request.POST.get('prioridade', 'normal'),
                responsavel=request.user,
                criado_por=request.user,
                data_planeamento=data_plan,
            )
            # Processar itens de material submetidos no formulário
            i = 1
            while True:
                material_id = request.POST.get(f'item_material_id_{i}')
                descricao = request.POST.get(f'item_desc_{i}')
                qtd_str = request.POST.get(f'item_qtd_{i}')
                if material_id is None and descricao is None:
                    break
                if descricao and qtd_str:
                    try:
                        qtd = float(qtd_str)
                    except (ValueError, TypeError):
                        qtd = None
                    if qtd:
                        material = None
                        if material_id:
                            material = Material.objects.filter(pk=material_id).first()
                        ItemProducao.objects.create(
                            ordem=op,
                            descricao=descricao,
                            quantidade=qtd,
                            material=material,
                        )
                i += 1
            num_itens = op.itens.count()
            messages.success(request, f'Ordem {referencia} criada com sucesso. ({num_itens} materiais registados)')
            return redirect('planeamento:ops')

    categorias = list(Categoria.objects.order_by('nome').values('id', 'nome'))
    return render(request, 'planeamento/ops/criar.html', {
        'clientes': clientes,
        'proxima_ref': proxima_ref,
        'categorias_json': json.dumps(categorias),
    })


@login_required
@departamento_required(['planeamento', 'direcao'])
def op_editar(request, pk):
    import json as _json
    ordem = get_object_or_404(OrdemProducao, pk=pk)
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cliente_id = request.POST.get('cliente', '').strip()

        if not nome or not cliente_id:
            messages.error(request, 'Nome da OP e cliente sao obrigatorios.')
        else:
            ordem.nome = nome
            ordem.cliente_id = cliente_id
            ordem.data_entrega_prevista = request.POST.get('data_entrega_prevista') or None
            ordem.prioridade = request.POST.get('prioridade', 'normal')
            ordem.save()

            # Substituir todos os itens pelos submetidos no formulário
            ordem.itens.all().delete()
            i = 1
            while True:
                material_id = request.POST.get(f'item_material_id_{i}')
                descricao = request.POST.get(f'item_desc_{i}')
                qtd_str = request.POST.get(f'item_qtd_{i}')
                if material_id is None and descricao is None:
                    break
                if descricao and qtd_str:
                    try:
                        qtd = float(qtd_str)
                    except (ValueError, TypeError):
                        qtd = None
                    if qtd:
                        material = None
                        if material_id:
                            material = Material.objects.filter(pk=material_id).first()
                        ItemProducao.objects.create(
                            ordem=ordem,
                            descricao=descricao,
                            quantidade=qtd,
                            material=material,
                        )
                i += 1

            messages.success(request, f'Ordem {ordem.referencia} atualizada.')
            return redirect('planeamento:ops')

    itens_existentes = list(
        ordem.itens.select_related('material').values(
            'id', 'descricao', 'quantidade', 'material__id', 'material__referencia', 'material__nome', 'material__unidade'
        )
    )
    categorias = list(Categoria.objects.order_by('nome').values('id', 'nome'))
    return render(request, 'planeamento/ops/editar.html', {
        'ordem': ordem,
        'clientes': clientes,
        'itens_json': json.dumps(itens_existentes, default=str),
        'categorias_json': json.dumps(categorias, default=str),
    })


@login_required
@departamento_required(['planeamento', 'direcao'])
def op_eliminar(request, pk):
    ordem = get_object_or_404(OrdemProducao, pk=pk)
    if request.method == 'POST':
        ref = ordem.referencia
        if request.user.is_direcao:
            # Eliminar registos relacionados (PROTECT) antes de apagar a OP
            ordem.expedicoes.all().delete()
            ordem.inspecoes.all().delete()
            ordem.pedidos_material.all().delete()
            ordem.tarefas_montagem.all().delete()
            ordem.itens.all().delete()
            ordem.delete()
            messages.success(request, f'Ordem {ref} eliminada.')
        else:
            try:
                ordem.delete()
                messages.success(request, f'Ordem {ref} eliminada.')
            except ProtectedError:
                messages.error(
                    request,
                    f'Não é possível eliminar a ordem {ref} porque existem registos associados '
                    f'(expedição, produção ou outros módulos) que dependem dela.'
                )
        return redirect('planeamento:ops')
    return redirect('planeamento:ops')


@login_required
@departamento_required(['planeamento', 'direcao'])
def cliente_criar_ajax(request):
    """Cria um cliente via AJAX a partir do modal."""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Metodo nao permitido.'}, status=405)

    nome = request.POST.get('nome', '').strip()
    if not nome:
        return JsonResponse({'erro': 'O nome do cliente e obrigatorio.'}, status=400)

    cliente = Cliente.objects.create(
        nome=nome,
        nif=request.POST.get('nif', '').strip(),
        email=request.POST.get('email', '').strip(),
        telefone=request.POST.get('telefone', '').strip(),
    )
    return JsonResponse({'id': cliente.pk, 'nome': cliente.nome})


@login_required
@departamento_required(['planeamento', 'direcao'])
def clientes_lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'planeamento/clientes/lista.html', {'clientes': clientes})
