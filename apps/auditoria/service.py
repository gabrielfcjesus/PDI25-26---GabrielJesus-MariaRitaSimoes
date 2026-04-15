"""
apps/auditoria/service.py
Serviço central de auditoria — ponto único de registo de logs.

Uso básico:
    from apps.auditoria.service import audit

    audit('criacao', request=request, modulo='planeamento',
          descricao='OP 2025-0001 criada', objeto=op)

    audit('edicao', request=request, modulo='armazem',
          descricao='Stock ajustado', old_data={'qty': 10}, new_data={'qty': 15})
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Campos cujos valores são mascarados antes de guardar
_CAMPOS_SENSIVEIS = frozenset({
    'password', 'passwd', 'senha', 'token', 'secret', 'key',
    'api_key', 'access_token', 'refresh_token', 'authorization',
    'credit_card', 'cvv', 'pin',
})


def _mascarar(data: Optional[dict]) -> Optional[dict]:
    """Substitui por '***' os valores de campos sensíveis."""
    if not isinstance(data, dict):
        return data
    return {
        k: '***' if k.lower() in _CAMPOS_SENSIVEIS else v
        for k, v in data.items()
    }


def _ip_do_request(request) -> Optional[str]:
    """Extrai o IP real do cliente, respeitando proxies."""
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def audit(
    acao: str,
    *,
    request=None,
    utilizador=None,
    modulo: str = '',
    descricao: str = '',
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
    objeto=None,
    extra: Optional[dict] = None,
    status_code: Optional[int] = None,
) -> None:
    """
    Cria um registo de auditoria.

    Nunca lança exceções — falhas internas são registadas no logger
    mas não interrompem o fluxo da aplicação.

    Parâmetros:
        acao        — código da ação (ver AuditLog.ACAO_CHOICES)
        request     — objeto HttpRequest (extrai IP, endpoint, método, user agent)
        utilizador  — instância de User; se None e request autenticado, usa request.user
        modulo      — nome do módulo (ex: 'planeamento', 'armazem')
        descricao   — texto legível descrevendo a ação
        old_data    — dicionário com estado anterior (será mascarado)
        new_data    — dicionário com estado novo (será mascarado)
        objeto      — instância de modelo associada ao evento
        extra       — dados adicionais livres (será mascarado)
        status_code — código HTTP resultante (útil para erros/acessos negados)
    """
    try:
        from .models import AuditLog
        from django.contrib.contenttypes.models import ContentType

        # Resolver utilizador
        user = utilizador
        if user is None and request is not None and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user

        # Preservar username para caso o utilizador seja eliminado futuramente
        username_cache = ''
        if user:
            username_cache = getattr(user, 'username', str(user))
        elif request is not None:
            # Para logins falhados, pode estar no POST
            username_cache = request.POST.get('username', '')[:150]

        # Dados do request
        ip = _ip_do_request(request)
        user_agent = ''
        endpoint = ''
        metodo = ''
        if request:
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:300]
            endpoint = request.path[:300]
            metodo = request.method

        # Associação genérica ao objeto
        ct = None
        oid = ''
        if objeto is not None:
            try:
                ct = ContentType.objects.get_for_model(objeto.__class__)
                oid = str(objeto.pk)
            except Exception:
                pass

        AuditLog.objects.create(
            utilizador=user,
            username_cache=username_cache,
            acao=acao,
            modulo=modulo,
            descricao=descricao,
            ip=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            metodo_http=metodo,
            status_code=status_code,
            old_data=_mascarar(old_data),
            new_data=_mascarar(new_data),
            extra=_mascarar(extra),
            content_type=ct,
            object_id=oid,
        )

    except Exception as exc:  # pragma: no cover
        logger.exception('Falha ao criar audit log [%s/%s]: %s', modulo, acao, exc)
