from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InspecaoQualidade
from apps.producao.models import OrdemProducao, RegistoProducao
from apps.core.permissions import departamento_required


@login_required
@departamento_required(["qualidade", "direcao"])
def menu(request):
    return render(request, "qualidade/menu.html")


@login_required
@departamento_required(["qualidade", "direcao"])
def inspecoes_lista(request):
    inspecoes = InspecaoQualidade.objects.select_related("ordem", "ordem__cliente", "inspector").all()
    return render(request, "qualidade/inspecoes/lista.html", {"inspecoes": inspecoes})


@login_required
@departamento_required(["qualidade", "direcao"])
def verificar(request):
    ordens = OrdemProducao.objects.filter(
        estado__in=["em_producao", "qualidade"]
    ).select_related("cliente").order_by("estado", "referencia")
    if request.method == "POST":
        ordem_id = request.POST.get("ordem")
        resultado = request.POST.get("resultado")
        tipo = request.POST.get("tipo", "final")
        obs = request.POST.get("observacoes", "")
        nc = request.POST.get("nao_conformidades", "")
        ac = request.POST.get("acoes_corretivas", "")
        if ordem_id and resultado:
            op = get_object_or_404(OrdemProducao, pk=ordem_id)
            InspecaoQualidade.objects.create(
                ordem=op, resultado=resultado, tipo=tipo,
                observacoes=obs, nao_conformidades=nc,
                acoes_corretivas=ac, inspector=request.user
            )
            resultado_label = dict(InspecaoQualidade.RESULTADO_CHOICES).get(resultado, resultado)

            if tipo == "intermedia":
                # Verif. intermédia — OP mantém-se em Qualidade independentemente do resultado
                if resultado == "reprovado":
                    RegistoProducao.objects.create(
                        ordem=op, utilizador=request.user,
                        descricao=f"Verificação intermédia: {resultado_label}. OP aguarda nova verificação.",
                    )
                    messages.warning(request, f"Verificação intermédia reprovada. OP {op.referencia} permanece em Qualidade.")
                else:
                    RegistoProducao.objects.create(
                        ordem=op, utilizador=request.user,
                        descricao=f"Verificação intermédia: {resultado_label}. OP disponível para Expedição com aviso.",
                    )
                    messages.success(request, f"Verificação intermédia registada. OP {op.referencia} pode avançar para Expedição (com aviso).")
            else:
                # Verif. final — determina avanço da OP
                if resultado in ("aprovado", "aprovado_condicional"):
                    op.estado = "expedicao"
                    op.save()
                    RegistoProducao.objects.create(
                        ordem=op, utilizador=request.user,
                        descricao=f"Verificação final: {resultado_label}. OP aprovada — disponível em Expedição.",
                    )
                    messages.success(request, f"OP {op.referencia} aprovada — disponível para criar guia de transporte.")
                else:
                    op.estado = "em_producao"
                    op.save()
                    RegistoProducao.objects.create(
                        ordem=op, utilizador=request.user,
                        descricao=f"Verificação final: {resultado_label}. OP devolvida à Produção.",
                    )
                    messages.warning(request, f"OP {op.referencia} reprovada — devolvida à Produção.")
            return redirect("qualidade:inspecoes")
    ops_em_producao_ids = list(
        ordens.filter(estado="em_producao").values_list('pk', flat=True)
    )
    return render(request, "qualidade/verificar.html", {
        "ordens": ordens,
        "ops_em_producao_ids": ops_em_producao_ids,
    })


@login_required
@departamento_required(["qualidade", "direcao"])
def op_detalhe(request, pk):
    op = get_object_or_404(
        OrdemProducao.objects.select_related('cliente', 'responsavel', 'criado_por'),
        pk=pk
    )
    itens = op.itens.select_related('material').all()
    inspecoes = op.inspecoes.select_related('inspector').order_by('-data')
    registos = op.registos.select_related('utilizador').order_by('-data')
    return render(request, "qualidade/op_detalhe.html", {
        'op': op,
        'itens': itens,
        'inspecoes': inspecoes,
        'registos': registos,
    })
