"""
apps/core/views.py
Views: autenticação, dashboard, gestão de utilizadores
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy

from .models import User, Departamento, Cargo
from .permissions import DepartamentoRequiredMixin, get_modulos_disponiveis
from .forms import LoginForm, UserCreateForm, UserUpdateForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user and user.ativo:
            login(request, user)
            return redirect(request.GET.get('next', 'core:dashboard'))
        messages.error(request, 'Credenciais inválidas ou utilizador inativo.')

    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('core:login')


@login_required
def dashboard(request):
    modulos = get_modulos_disponiveis(request.user)
    context = {
        'modulos': modulos,
        'titulo': 'Dashboard',
    }
    return render(request, 'core/dashboard.html', context)


class UtilizadoresListView(DepartamentoRequiredMixin, ListView):
    """Lista de utilizadores - apenas Direção e RH"""
    model = User
    template_name = 'core/utilizadores/lista.html'
    context_object_name = 'utilizadores'
    departamentos_permitidos = ['rh', 'direcao']

    def get_queryset(self):
        qs = User.objects.select_related('departamento', 'cargo')
        q = self.request.GET.get('q', '').strip()
        dep_id = self.request.GET.get('departamento', '')
        if q:
            from django.db.models import Q
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q))
        if dep_id:
            qs = qs.filter(departamento_id=dep_id)
        return qs.order_by('username')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departamentos'] = Departamento.objects.order_by('nome')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['dep_id'] = self.request.GET.get('departamento', '')
        return ctx


class UtilizadorCreateView(DepartamentoRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'core/utilizadores/form.html'
    success_url = reverse_lazy('core:utilizadores')
    departamentos_permitidos = ['direcao']

    def form_valid(self, form):
        messages.success(self.request, 'Utilizador criado com sucesso.')
        return super().form_valid(form)


class UtilizadorUpdateView(DepartamentoRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'core/utilizadores/form.html'
    success_url = reverse_lazy('core:utilizadores')
    departamentos_permitidos = ['direcao', 'rh']

    def form_valid(self, form):
        messages.success(self.request, 'Utilizador atualizado com sucesso.')
        return super().form_valid(form)


@login_required
def perfil_view(request):
    return render(request, 'core/perfil.html', {'titulo': 'O meu perfil'})


@login_required
def relatorios(request):
    import json
    from datetime import date, datetime, timedelta
    from django.db.models import Count, Q
    from apps.producao.models import OrdemProducao
    from apps.expedicao.models import Expedicao
    from apps.qualidade.models import InspecaoQualidade
    from apps.armazem.models import Material

    # Intervalo de tempo (padrão: últimos 30 dias)
    hoje = date.today()
    data_inicio_str = request.GET.get('data_inicio', '').strip()
    data_fim_str = request.GET.get('data_fim', '').strip()

    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date() if data_inicio_str else hoje - timedelta(days=30)
    except ValueError:
        data_inicio = hoje - timedelta(days=30)

    try:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else hoje
    except ValueError:
        data_fim = hoje

    # Querysets filtrados pelo intervalo
    ops_qs = OrdemProducao.objects.filter(criado_em__date__gte=data_inicio, criado_em__date__lte=data_fim)
    exp_qs = Expedicao.objects.filter(criado_em__date__gte=data_inicio, criado_em__date__lte=data_fim)
    insp_qs = InspecaoQualidade.objects.filter(data__date__gte=data_inicio, data__date__lte=data_fim)

    # KPIs
    total_ops = ops_qs.count()
    em_producao = ops_qs.filter(estado='em_producao').count()
    concluidas = ops_qs.filter(estado='concluida').count()
    guias_ativas = exp_qs.exclude(estado='entregue').count()

    # OPs por estado
    estados_op = dict(OrdemProducao.ESTADO_CHOICES)
    ops_por_estado = {}
    for k, v in estados_op.items():
        c = ops_qs.filter(estado=k).count()
        if c > 0:
            ops_por_estado[v] = c

    # Expedições por estado
    estados_exp = dict(Expedicao.ESTADO_CHOICES)
    exp_por_estado = {}
    for k, v in estados_exp.items():
        c = exp_qs.filter(estado=k).count()
        if c > 0:
            exp_por_estado[v] = c

    # Inventário (snapshot atual, não filtrado por data)
    mats = Material.objects.filter(ativo=True)
    sem_stock = mats.filter(stock_atual=0).count()
    baixo = 0
    normal = 0
    for m in mats.exclude(stock_atual=0):
        if m.stock_minimo and m.stock_atual <= m.stock_minimo:
            baixo += 1
        else:
            normal += 1

    inventario = {}
    if normal:
        inventario['Normal'] = normal
    if baixo:
        inventario['Baixo Stock'] = baixo
    if sem_stock:
        inventario['Sem Stock'] = sem_stock

    # Resultados qualidade
    insp = insp_qs.values('resultado').annotate(total=Count('resultado'))
    labels_qual = {'aprovado': 'Aprovado', 'reprovado': 'Reprovado', 'aprovado_condicional': 'Aprovado Cond.'}
    qualidade = {labels_qual[r['resultado']]: r['total'] for r in insp if r['resultado'] in labels_qual}

    # Pesquisa de OP com timeline (independente do intervalo)
    q = request.GET.get('q', '').strip()
    ops_timeline = []
    if q:
        ops_found = OrdemProducao.objects.select_related('cliente', 'criado_por').filter(
            Q(referencia__icontains=q) | Q(nome__icontains=q)
        ).prefetch_related('inspecoes', 'expedicoes')
        for op in ops_found:
            inspecao = op.inspecoes.order_by('data').last()
            expedicao = op.expedicoes.order_by('criado_em').first()
            ops_timeline.append({
                'op': op,
                'planeamento_em': op.data_planeamento or op.criado_em,
                'producao_inicio': op.data_real_inicio,
                'producao_fim': op.data_real_fim,
                'qualidade_em': inspecao.data if inspecao else None,
                'qualidade_resultado': inspecao.get_resultado_display() if inspecao else None,
                'qualidade_inspector': inspecao.inspector if inspecao else None,
                'expedicao_em': expedicao.criado_em if expedicao else None,
                'expedicao_ref': expedicao.referencia if expedicao else None,
                'expedicao_responsavel': expedicao.responsavel if expedicao else None,
            })

    context = {
        'kpis': [
            ('Total OPs', total_ops, '#7ec8e3'),
            ('Em Produção', em_producao, '#f4b97f'),
            ('Concluídas', concluidas, '#a5d6a7'),
            ('Guias Ativas', guias_ativas, '#b39ddb'),
        ],
        'ops_por_estado_json': json.dumps(ops_por_estado),
        'exp_por_estado_json': json.dumps(exp_por_estado),
        'inventario_json': json.dumps(inventario),
        'qualidade_json': json.dumps(qualidade),
        'ops_timeline': ops_timeline,
        'q': q,
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'data_inicio_display': data_inicio.strftime('%d/%m/%Y'),
        'data_fim_display': data_fim.strftime('%d/%m/%Y'),
    }
    return render(request, 'core/relatorios.html', context)


@login_required
def ops_sugestoes(request):
    """AJAX: devolve sugestões de OPs para o live search dos relatórios."""
    from django.http import JsonResponse
    from django.db.models import Q
    from apps.producao.models import OrdemProducao
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'resultados': []})
    ops = OrdemProducao.objects.select_related('cliente').filter(
        Q(referencia__icontains=q) | Q(nome__icontains=q)
    ).order_by('-criado_em')[:10]
    resultados = [
        {
            'referencia': op.referencia,
            'nome': op.nome,
            'cliente': op.cliente.nome if op.cliente else '',
            'estado': op.get_estado_display(),
        }
        for op in ops
    ]
    return JsonResponse({'resultados': resultados})
