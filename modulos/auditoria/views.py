from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from modulos.core.permissions import departamento_required
from modulos.core.models import User
from .models import AuditLog


@login_required
@departamento_required(['direcao'])
def logs_lista(request):
    qs = AuditLog.objects.select_related('utilizador').order_by('-timestamp')

    acao = request.GET.get('acao', '').strip()
    modulo = request.GET.get('modulo', '').strip()
    utilizador_id = request.GET.get('utilizador', '').strip()
    data_inicio = request.GET.get('data_inicio', '').strip()
    data_fim = request.GET.get('data_fim', '').strip()
    pesquisa = request.GET.get('q', '').strip()

    if acao:
        qs = qs.filter(acao=acao)
    if modulo:
        qs = qs.filter(modulo=modulo)
    if utilizador_id:
        qs = qs.filter(utilizador_id=utilizador_id)
    if data_inicio:
        qs = qs.filter(timestamp__date__gte=data_inicio)
    if data_fim:
        qs = qs.filter(timestamp__date__lte=data_fim)
    if pesquisa:
        qs = qs.filter(descricao__icontains=pesquisa)

    total = qs.count()
    logs = qs[:500]

    modulos_disponiveis = (
        AuditLog.objects
        .values_list('modulo', flat=True)
        .distinct()
        .order_by('modulo')
    )
    utilizadores = User.objects.filter(ativo=True).order_by('username')

    return render(request, 'auditoria/logs_lista.html', {
        'logs': logs,
        'total': total,
        'acoes': AuditLog.ACAO_CHOICES,
        'modulos': modulos_disponiveis,
        'utilizadores': utilizadores,
        'filtros': {
            'acao': acao,
            'modulo': modulo,
            'utilizador': utilizador_id,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'q': pesquisa,
        },
    })


@login_required
@departamento_required(['direcao'])
def log_detalhe(request, pk):
    log = get_object_or_404(AuditLog, pk=pk)
    return render(request, 'auditoria/log_detalhe.html', {'log': log})
