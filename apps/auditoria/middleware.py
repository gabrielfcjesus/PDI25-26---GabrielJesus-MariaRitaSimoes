"""
apps/auditoria/middleware.py
Middleware que regista automaticamente acessos negados e erros de servidor.
"""
from .service import audit


def _modulo_from_path(path: str) -> str:
    """Extrai o nome do módulo a partir do URL path."""
    parts = [p for p in path.strip('/').split('/') if p]
    return parts[0] if parts else 'core'


class AuditMiddleware:
    """
    Regista automaticamente:
      - Respostas 403 (acesso negado)
      - Exceções não tratadas (erros 500)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 403:
            audit(
                'acesso_negado',
                request=request,
                modulo=_modulo_from_path(request.path),
                descricao=f'Acesso negado a {request.path}',
                status_code=403,
            )

        return response

    def process_exception(self, request, exception):
        """Chamado pelo Django quando uma view lança uma exceção não tratada."""
        audit(
            'erro',
            request=request,
            modulo=_modulo_from_path(request.path),
            descricao=f'{type(exception).__name__}: {str(exception)[:300]}',
            status_code=500,
        )
        return None  # Deixa o Django continuar o processamento normal do erro
